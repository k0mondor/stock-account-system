from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import AccountStatus, AssociationStatus, PasswordType
from app.core.auth_tokens import issue_access_token
from app.core.config import settings
from app.core.security import hash_password, verify_password
from app.models.association import AccountAssociation
from app.models.fund_account import FundAccount
from app.models.security_account import SecuritiesAccount
from app.services.operation_log_service import add_operation_log


def login(db: Session, fund_account_id: str, password: str) -> dict:
    account = db.scalar(
        select(FundAccount).where(FundAccount.fund_account_id == fund_account_id)
    )
    if not account or not verify_password(password, account.trade_password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="资金账户号或交易密码错误",
        )
    if account.account_status != AccountStatus.NORMAL.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"资金账户状态为 {account.account_status}，不允许登录",
        )

    associations = list(db.scalars(
        select(AccountAssociation).where(
            AccountAssociation.fund_account_id == fund_account_id,
            AccountAssociation.association_status == AssociationStatus.ACTIVE.value,
        )
    ).all())
    if not associations:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="资金账户未绑定有效证券账户",
        )
    if len(associations) != 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="资金账户关联不满足一对一唯一有效约束",
        )
    association = associations[0]
    security_account = db.get(SecuritiesAccount, association.security_account_id)
    if not security_account:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="关联证券账户不存在",
        )
    if (
        association.investor_id != account.investor_id
        or security_account.investor_id != account.investor_id
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="账户关联中的投资者归属不一致",
        )
    if security_account.account_status != AccountStatus.NORMAL.value:
        current_status = (
            security_account.account_status if security_account else "NOT_FOUND"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"证券账户状态为 {current_status}，不允许登录",
        )

    expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.access_token_expire_hours)
    return {
        "verified": True,
        "investor_id": account.investor_id,
        "fund_account_id": account.fund_account_id,
        "security_account_id": association.security_account_id,
        "first_login": False,
        "token": issue_access_token(
            investor_id=account.investor_id,
            fund_account_id=account.fund_account_id,
            security_account_id=association.security_account_id,
            expires_at=int(expires_at.timestamp()),
        ),
        "expires_at": expires_at,
    }


def change_password(
    db: Session,
    *,
    fund_account_id: str,
    password_type: PasswordType,
    old_password: str,
    new_password: str,
) -> FundAccount:
    account = db.scalar(
        select(FundAccount)
        .where(FundAccount.fund_account_id == fund_account_id)
        .with_for_update()
    )
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="资金账户不存在")
    if account.account_status != AccountStatus.NORMAL.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"资金账户状态为 {account.account_status}，不允许修改密码",
        )

    if password_type == PasswordType.TRADE:
        old_hash = account.trade_password_hash
    else:
        old_hash = account.withdraw_password_hash
    if not verify_password(old_password, old_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="原密码错误",
        )
    if verify_password(new_password, old_hash):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="新密码不能与原密码相同",
        )

    new_hash = hash_password(new_password)
    if password_type == PasswordType.TRADE:
        account.trade_password_hash = new_hash
    else:
        account.withdraw_password_hash = new_hash

    add_operation_log(
        db,
        operator_id=account.investor_id,
        operator_name="投资者",
        operation_type="CHANGE_PASSWORD",
        target_type="FUND",
        target_id=fund_account_id,
        operation_detail=f"修改{password_type.value}密码",
    )
    db.flush()
    return account
