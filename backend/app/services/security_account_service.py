from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import AccountStatus, AssociationStatus
from app.core.time import utc_now
from app.models.association import AccountAssociation
from app.models.base_data import Customer
from app.models.security_account import SecuritiesAccount
from app.models.security_position import SecurityPosition
from app.services.account_state_service import record_status_change
from app.services.operation_log_service import add_operation_log


def create_security_account(
    db: Session,
    *,
    security_account_id: str,
    investor_id: str,
) -> SecuritiesAccount:
    account = SecuritiesAccount(
        security_account_id=security_account_id,
        investor_id=investor_id,
    )
    db.add(account)
    db.flush()
    return account


def list_security_accounts(
    db: Session,
    *,
    investor_id: str | None = None,
    account_status: str | None = None,
) -> list[SecuritiesAccount]:
    query = select(SecuritiesAccount).order_by(SecuritiesAccount.created_at.desc())
    if investor_id:
        query = query.where(SecuritiesAccount.investor_id == investor_id)
    if account_status:
        query = query.where(SecuritiesAccount.account_status == account_status)
    return list(db.scalars(query).all())


def get_security_account(
    db: Session, security_account_id: str
) -> SecuritiesAccount:
    account = db.get(SecuritiesAccount, security_account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="证券账户不存在",
        )
    return account


def close_security_account(
    db: Session,
    security_account_id: str,
    *,
    customer_id_number: str,
    operator_id: str,
    operator_name: str,
) -> SecuritiesAccount:
    account = db.scalar(
        select(SecuritiesAccount)
        .where(SecuritiesAccount.security_account_id == security_account_id)
        .with_for_update()
    )
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="证券账户不存在",
        )
    if account.account_status != AccountStatus.NORMAL.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"证券账户状态为 {account.account_status}，不能注销",
        )
    customer = db.get(Customer, account.investor_id)
    if not customer or customer.id_number != customer_id_number:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="客户身份信息与证券账户不匹配",
        )
    position = db.scalar(
        select(SecurityPosition).where(
            SecurityPosition.security_account_id == security_account_id,
            SecurityPosition.total_quantity > 0,
        )
    )
    if position:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="证券账户仍有持仓，不能注销",
        )

    associations = list(db.scalars(
        select(AccountAssociation).where(
            AccountAssociation.security_account_id == security_account_id,
            AccountAssociation.association_status == AssociationStatus.ACTIVE.value,
        )
    ).all())
    if len(associations) > 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="证券账户存在多个有效绑定，请先修复关联数据",
        )
    for association in associations:
        association.association_status = AssociationStatus.UNLINKED.value
        now = utc_now()
        association.disassociated_at = now
        association.updated_at = now

    previous_status = account.account_status
    account.account_status = AccountStatus.CLOSED.value
    record_status_change(
        db,
        account_type="SECURITY",
        account_id=security_account_id,
        previous_status=previous_status,
        target_status=AccountStatus.CLOSED.value,
        reason="证券账户销户",
        operator_id=operator_id,
        operator_name=operator_name,
        log_operation=False,
    )
    add_operation_log(
        db,
        operator_id=operator_id,
        operator_name=operator_name,
        operation_type="CLOSE_SECURITY_ACCOUNT",
        target_type="SECURITY",
        target_id=security_account_id,
        operation_detail="注销证券账户并解除当前有效绑定关系",
    )
    db.flush()
    return account
