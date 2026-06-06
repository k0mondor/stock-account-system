from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import AccountStatus, AssociationStatus
from app.core.time import utc_now
from app.models.association import AccountAssociation
from app.models.base_data import Customer
from app.models.fund_account import AccountStateChangeRecord, FundAccount
from app.models.security_account import SecuritiesAccount
from app.services.operation_log_service import add_operation_log


def _new_id(prefix: str) -> str:
    return f"{prefix}{uuid4().hex[:18].upper()}"


ALLOWED_TRANSITIONS = {
    AccountStatus.NORMAL.value: {
        AccountStatus.FROZEN.value,
        AccountStatus.LOST.value,
        AccountStatus.CLOSED.value,
    },
    AccountStatus.FROZEN.value: {AccountStatus.NORMAL.value},
    AccountStatus.LOST.value: {AccountStatus.NORMAL.value},
}


def _was_frozen_by_fund_loss(
    db: Session,
    security_account_id: str,
) -> bool:
    latest_change = db.scalar(
        select(AccountStateChangeRecord)
        .where(
            AccountStateChangeRecord.account_type == "SECURITY",
            AccountStateChangeRecord.account_id == security_account_id,
        )
        .order_by(AccountStateChangeRecord.changed_at.desc())
        .limit(1)
    )
    return bool(
        latest_change
        and latest_change.target_status == AccountStatus.FROZEN.value
        and latest_change.reason == "关联资金账户挂失"
    )


def record_status_change(
    db: Session,
    *,
    account_type: str,
    account_id: str,
    previous_status: str,
    target_status: str,
    reason: str | None,
    operator_id: str,
    operator_name: str,
    log_operation: bool = True,
) -> None:
    db.add(
        AccountStateChangeRecord(
            change_id=_new_id("STC"),
            account_type=account_type,
            account_id=account_id,
            previous_status=previous_status,
            target_status=target_status,
            reason=reason,
            operator_id=operator_id,
            operator_name=operator_name,
            changed_at=utc_now(),
        )
    )
    if log_operation:
        add_operation_log(
            db,
            operator_id=operator_id,
            operator_name=operator_name,
            operation_type=f"{account_type}_{target_status}",
            target_type=account_type,
            target_id=account_id,
            operation_detail=(
                f"账户状态由 {previous_status} 变更为 {target_status}"
                + (f"，原因：{reason}" if reason else "")
            ),
        )


def list_status_history(
    db: Session,
    *,
    account_type: str,
    account_id: str,
) -> list[AccountStateChangeRecord]:
    normalized_type = (
        "SECURITY"
        if account_type.upper() in {"SECURITY", "SECURITIES"}
        else account_type.upper()
    )
    if normalized_type not in {"FUND", "SECURITY"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户类型仅支持 FUND 或 SECURITY",
        )
    return list(
        db.scalars(
            select(AccountStateChangeRecord)
            .where(
                AccountStateChangeRecord.account_type == normalized_type,
                AccountStateChangeRecord.account_id == account_id,
            )
            .order_by(AccountStateChangeRecord.changed_at.desc())
        ).all()
    )


def _set_status(
    db: Session,
    account,
    *,
    account_type: str,
    account_id: str,
    target_status: AccountStatus,
    reason: str | None,
    operator_id: str,
    operator_name: str,
) -> None:
    previous_status = account.account_status
    if target_status.value not in ALLOWED_TRANSITIONS.get(previous_status, set()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"不允许从 {previous_status} 变更为 {target_status.value}",
        )
    account.account_status = target_status.value
    record_status_change(
        db,
        account_type=account_type,
        account_id=account_id,
        previous_status=previous_status,
        target_status=target_status.value,
        reason=reason,
        operator_id=operator_id,
        operator_name=operator_name,
    )


def change_status(
    db: Session,
    *,
    account_type: str,
    account_id: str,
    target_status: AccountStatus,
    customer_id_number: str | None = None,
    reason: str | None,
    operator_id: str,
    operator_name: str,
) -> FundAccount | SecuritiesAccount:
    normalized_type = "SECURITY" if account_type.upper() in {"SECURITY", "SECURITIES"} else account_type.upper()
    model = FundAccount if normalized_type == "FUND" else SecuritiesAccount if normalized_type == "SECURITY" else None
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户类型仅支持 FUND 或 SECURITY",
        )

    primary_key = (
        FundAccount.fund_account_id
        if normalized_type == "FUND"
        else SecuritiesAccount.security_account_id
    )
    account = db.scalar(
        select(model).where(primary_key == account_id).with_for_update()
    )
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="账户不存在")
    if target_status == AccountStatus.CLOSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="销户必须使用对应账户的销户接口",
        )
    identity_required = (
        target_status == AccountStatus.LOST
        or (
            account.account_status == AccountStatus.LOST.value
            and target_status == AccountStatus.NORMAL
        )
    )
    if identity_required:
        customer = db.get(Customer, account.investor_id)
        if (
            not customer
            or not customer_id_number
            or customer.id_number != customer_id_number
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="客户身份信息与账户不匹配",
            )

    _set_status(
        db,
        account,
        account_type=normalized_type,
        account_id=account_id,
        target_status=target_status,
        reason=reason,
        operator_id=operator_id,
        operator_name=operator_name,
    )

    # 资金账户挂失时同步限制关联证券账户交易能力；补办时仅恢复由该流程冻结的账户。
    if normalized_type == "FUND" and target_status in {
        AccountStatus.LOST,
        AccountStatus.NORMAL,
    }:
        association = db.scalar(
            select(AccountAssociation).where(
                AccountAssociation.fund_account_id == account_id,
                AccountAssociation.association_status == AssociationStatus.ACTIVE.value,
            )
        )
        if association:
            security_account = db.scalar(
                select(SecuritiesAccount)
                .where(
                    SecuritiesAccount.security_account_id
                    == association.security_account_id
                )
                .with_for_update()
            )
            if (
                target_status == AccountStatus.LOST
                and security_account.account_status == AccountStatus.NORMAL.value
            ):
                _set_status(
                    db,
                    security_account,
                    account_type="SECURITY",
                    account_id=security_account.security_account_id,
                    target_status=AccountStatus.FROZEN,
                    reason="关联资金账户挂失",
                    operator_id=operator_id,
                    operator_name=operator_name,
                )
            elif (
                target_status == AccountStatus.NORMAL
                and security_account.account_status == AccountStatus.FROZEN.value
                and _was_frozen_by_fund_loss(
                    db, security_account.security_account_id
                )
            ):
                _set_status(
                    db,
                    security_account,
                    account_type="SECURITY",
                    account_id=security_account.security_account_id,
                    target_status=AccountStatus.NORMAL,
                    reason="关联资金账户挂失补办完成",
                    operator_id=operator_id,
                    operator_name=operator_name,
                )

    db.flush()
    return account
