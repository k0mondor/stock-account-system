from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import AccountStatus
from app.models.security_account import SecuritiesAccount


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
    del db, security_account_id, customer_id_number, operator_id, operator_name
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="请使用联合销户接口",
    )
