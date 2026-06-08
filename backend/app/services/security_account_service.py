from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import AccountStatus, AssociationStatus
from app.core.security import hash_password
from app.core.time import utc_now
from app.models.association import AccountAssociation
from app.models.base_data import Customer, Staff
from app.models.security_account import SecuritiesAccount
from app.models.security_position import SecurityPosition
from app.services.account_state_service import record_status_change
from app.services.operation_log_service import add_operation_log
from app.core.enums import PasswordType, StaffRole, StaffStatus


def create_security_account(
    db: Session,
    *,
    security_account_id: str,
    investor_id: str,
    security_password: str,
) -> SecuritiesAccount:
    account = SecuritiesAccount(
        security_account_id=security_account_id,
        investor_id=investor_id,
        security_password_hash=hash_password(security_password),
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


def reset_password_by_staff(
    db: Session,
    security_account_id: str,
    *,
    staff_id: str,
    customer_id_number: str,
    new_password: str,
    reason: str,
) -> SecuritiesAccount:
    from app.services.association_service import require_active_association_for_security

    require_active_association_for_security(
        db,
        security_account_id=security_account_id,
        operation_type="CHANGE_PWD",
    )
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
            detail=f"证券账户状态为 {account.account_status}，不允许修改密码",
        )
    staff = db.get(Staff, staff_id)
    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="工作人员不存在")
    if staff.staff_status != StaffStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="工作人员状态不可用",
        )
    if staff.role not in {StaffRole.STAFF.value, StaffRole.ADMIN.value}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="当前工作人员无密码重置权限",
        )

    customer = db.get(Customer, account.investor_id)
    if not customer or customer.id_number != customer_id_number:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="客户身份信息与证券账户不匹配",
        )

    account.security_password_hash = hash_password(new_password)
    add_operation_log(
        db,
        operator_id=staff.staff_id,
        operator_name=staff.staff_name,
        operation_type="RESET_PASSWORD",
        target_type="SECURITY",
        target_id=security_account_id,
        operation_detail=f"代理重置{PasswordType.TRADE.value}密码，原因：{reason}",
    )
    db.flush()
    return account
