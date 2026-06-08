from dataclasses import dataclass
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.enums import AccountStatus, AssociationStatus
from app.core.time import utc_now
from app.models.association import AccountAssociation
from app.models.base_data import Customer
from app.models.fund_account import FundAccount
from app.models.security_account import SecuritiesAccount
from app.models.security_position import SecurityPosition
from app.services.account_state_service import record_status_change
from app.services.operation_log_service import add_operation_log

@dataclass
class JointAccountPair:
    customer: Customer
    fund_account: FundAccount
    security_account: SecuritiesAccount
    association: AccountAssociation


def validate_joint_account_pair(
    db: Session,
    *,
    fund_account_id: str,
    security_account_id: str,
    customer_id_number: str | None = None,
) -> JointAccountPair:
    fund_account = db.scalar(
        select(FundAccount)
        .where(FundAccount.fund_account_id == fund_account_id)
        .with_for_update()
    )
    if not fund_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="资金账户不存在")

    security_account = db.scalar(
        select(SecuritiesAccount)
        .where(SecuritiesAccount.security_account_id == security_account_id)
        .with_for_update()
    )
    if not security_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="证券账户不存在")

    if fund_account.investor_id != security_account.investor_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="资金账户与证券账户不属于同一投资者",
        )

    customer = db.get(Customer, fund_account.investor_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="账户归属的投资者档案不存在",
        )
    if customer_id_number and customer.id_number != customer_id_number:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="客户证件号与账户归属不一致",
        )

    associations = list(
        db.scalars(
            select(AccountAssociation)
            .where(
                AccountAssociation.fund_account_id == fund_account_id,
                AccountAssociation.security_account_id == security_account_id,
                AccountAssociation.association_status == AssociationStatus.ACTIVE.value,
            )
            .with_for_update()
        ).all()
    )
    active_fund_count = db.scalar(
        select(func.count()).select_from(AccountAssociation).where(
            AccountAssociation.fund_account_id == fund_account_id,
            AccountAssociation.association_status == AssociationStatus.ACTIVE.value,
        )
    )
    active_security_count = db.scalar(
        select(func.count()).select_from(AccountAssociation).where(
            AccountAssociation.security_account_id == security_account_id,
            AccountAssociation.association_status == AssociationStatus.ACTIVE.value,
        )
    )
    if len(associations) != 1 or active_fund_count != 1 or active_security_count != 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="当前账户对不存在唯一有效绑定",
        )

    association = associations[0]
    if association.investor_id != customer.customer_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="绑定关系中的投资者归属与账户不一致",
        )

    return JointAccountPair(
        customer=customer,
        fund_account=fund_account,
        security_account=security_account,
        association=association,
    )


def validate_joint_close_preconditions(
    db: Session,
    pair: JointAccountPair,
) -> None:
    if pair.fund_account.account_status != AccountStatus.NORMAL.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="联合销户前，资金账户状态必须为 NORMAL",
        )
    if pair.security_account.account_status != AccountStatus.NORMAL.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="联合销户前，证券账户状态必须为 NORMAL",
        )

    zero = Decimal("0.00")
    if (
        pair.fund_account.available_balance != zero
        or pair.fund_account.frozen_amount != zero
        or pair.fund_account.total_amount != zero
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="联合销户前，资金账户余额、冻结金额、总金额必须全部清零",
        )

    has_position = pair_has_position(db, pair)
    if has_position:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="联合销户前，证券账户必须无持仓、无冻结证券",
        )


def pair_has_position(db: Session, pair: JointAccountPair) -> bool:
    position = db.scalar(
        select(SecurityPosition).where(
            SecurityPosition.security_account_id == pair.security_account.security_account_id,
            (SecurityPosition.total_quantity > 0)
            | (SecurityPosition.frozen_quantity > 0),
        )
    )
    return position is not None


def close_joint_account_pair(
    db: Session,
    *,
    pair: JointAccountPair,
    operator_id: str,
    operator_name: str,
    reason: str | None,
):
    closed_at = utc_now()
    pair.association.association_status = AssociationStatus.UNLINKED.value
    pair.association.disassociated_at = closed_at
    pair.association.updated_at = closed_at

    fund_previous_status = pair.fund_account.account_status
    security_previous_status = pair.security_account.account_status
    pair.fund_account.account_status = AccountStatus.CLOSED.value
    pair.security_account.account_status = AccountStatus.CLOSED.value

    close_reason = reason or "联合销户"
    record_status_change(
        db,
        account_type="FUND",
        account_id=pair.fund_account.fund_account_id,
        previous_status=fund_previous_status,
        target_status=AccountStatus.CLOSED.value,
        reason=close_reason,
        operator_id=operator_id,
        operator_name=operator_name,
        log_operation=False,
    )
    record_status_change(
        db,
        account_type="SECURITY",
        account_id=pair.security_account.security_account_id,
        previous_status=security_previous_status,
        target_status=AccountStatus.CLOSED.value,
        reason=close_reason,
        operator_id=operator_id,
        operator_name=operator_name,
        log_operation=False,
    )
    add_operation_log(
        db,
        operator_id=operator_id,
        operator_name=operator_name,
        operation_type="JOINT_CLOSE",
        target_type="ASSOCIATION",
        target_id=pair.association.association_id,
        operation_detail=(
            f"联合销户完成，资金账户 {pair.fund_account.fund_account_id}、"
            f"证券账户 {pair.security_account.security_account_id} 已关闭"
            + (f"，原因：{reason}" if reason else "")
        ),
    )
    db.flush()
    return closed_at


def close_joint_accounts(
    db: Session,
    *,
    fund_account_id: str,
    security_account_id: str,
    customer_id_number: str,
    operator_id: str,
    operator_name: str,
    reason: str | None,
) -> dict:
    pair = validate_joint_account_pair(
        db,
        fund_account_id=fund_account_id,
        security_account_id=security_account_id,
        customer_id_number=customer_id_number,
    )
    validate_joint_close_preconditions(db, pair)
    closed_at = close_joint_account_pair(
        db,
        pair=pair,
        operator_id=operator_id,
        operator_name=operator_name,
        reason=reason,
    )
    return {
        "association_id": pair.association.association_id,
        "investor_id": pair.customer.customer_id,
        "fund_account_id": pair.fund_account.fund_account_id,
        "security_account_id": pair.security_account.security_account_id,
        "association_status": AssociationStatus.UNLINKED,
        "fund_account_status": AccountStatus.CLOSED,
        "security_account_status": AccountStatus.CLOSED,
        "closed_at": closed_at,
    }
