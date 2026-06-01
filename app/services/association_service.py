"""账户关联业务逻辑"""

from sqlalchemy.orm import Session
from app.crud import association as association_crud
from app.crud import fund_account as fund_account_crud
from app.crud import security_account as security_account_crud
from app.utils.exceptions import NotFoundException
from app.utils.constants import AssociationStatus, AccountStatus


def get_association_info(
    db: Session,
    fund_account_id: str = None,
    security_account_id: str = None,
    investor_id: str = None,
) -> dict:
    """查询账户关联"""
    association = association_crud.get_association(
        db=db,
        fund_account_id=fund_account_id,
        security_account_id=security_account_id,
        investor_id=investor_id,
    )
    
    if not association:
        return {
            "association_id": None,
            "investor_id": None,
            "fund_account_id": fund_account_id,
            "security_account_id": security_account_id,
            "association_status": AssociationStatus.UNLINKED.value,
            "associated_at": None,
        }
    
    return {
        "association_id": association.association_id,
        "investor_id": association.investor_id,
        "fund_account_id": association.fund_account_id,
        "security_account_id": association.security_account_id,
        "association_status": association.association_status.value,
        "associated_at": association.associated_at,
    }


def check_association(
    db: Session,
    fund_account_id: str,
    security_account_id: str,
    operation_type: str,
    investor_id: str = None,
) -> dict:
    """账户关联业务校验"""
    # 检查关联
    is_associated = association_crud.check_association_exists(
        db=db,
        fund_account_id=fund_account_id,
        security_account_id=security_account_id,
    )
    
    if not is_associated:
        return {
            "is_valid": False,
            "association_status": AssociationStatus.UNLINKED.value,
            "fund_account_status": AccountStatus.NORMAL.value,
            "security_account_status": AccountStatus.NORMAL.value,
            "is_operation_allowed": False,
            "error_message": "账户未关联或关联无效",
        }
    
    # 获取账户状态
    fund_account = fund_account_crud.get_fund_account(db, fund_account_id)
    security_account = security_account_crud.get_security_account(db, security_account_id)
    
    if not fund_account or not security_account:
        return {
            "is_valid": False,
            "association_status": AssociationStatus.ACTIVE.value,
            "fund_account_status": fund_account.status.value if fund_account else "UNKNOWN",
            "security_account_status": security_account.status.value if security_account else "UNKNOWN",
            "is_operation_allowed": False,
            "error_message": "账户不存在",
        }
    
    # 检查账户状态
    fund_status_ok = fund_account.status == AccountStatus.NORMAL
    security_status_ok = security_account.status == AccountStatus.NORMAL
    
    is_operation_allowed = fund_status_ok and security_status_ok
    
    error_message = None
    if not fund_status_ok:
        error_message = f"资金账户状态异常: {fund_account.status.value}"
    elif not security_status_ok:
        error_message = f"证券账户状态异常: {security_account.status.value}"
    
    return {
        "is_valid": True,
        "association_status": AssociationStatus.ACTIVE.value,
        "fund_account_status": fund_account.status.value,
        "security_account_status": security_account.status.value,
        "is_operation_allowed": is_operation_allowed,
        "error_message": error_message,
    }
