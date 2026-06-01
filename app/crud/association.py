"""账户关联数据访问层"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import AccountAssociation
from app.utils.constants import AssociationStatus


def create_association(
    db: Session,
    association_id: str,
    investor_id: str,
    fund_account_id: str,
    security_account_id: str,
    remark: str = None,
) -> AccountAssociation:
    """创建账户关联"""
    association = AccountAssociation(
        association_id=association_id,
        investor_id=investor_id,
        fund_account_id=fund_account_id,
        security_account_id=security_account_id,
        association_status=AssociationStatus.ACTIVE,
        remark=remark,
    )
    db.add(association)
    db.commit()
    db.refresh(association)
    return association


def get_association_by_fund_account(
    db: Session,
    fund_account_id: str,
) -> AccountAssociation | None:
    """通过资金账户获取关联"""
    return db.query(AccountAssociation).filter(
        AccountAssociation.fund_account_id == fund_account_id
    ).first()


def get_association_by_security_account(
    db: Session,
    security_account_id: str,
) -> AccountAssociation | None:
    """通过证券账户获取关联"""
    return db.query(AccountAssociation).filter(
        AccountAssociation.security_account_id == security_account_id
    ).first()


def get_association_by_investor(
    db: Session,
    investor_id: str,
) -> AccountAssociation | None:
    """通过投资者ID获取关联"""
    return db.query(AccountAssociation).filter(
        AccountAssociation.investor_id == investor_id
    ).first()


def get_association(
    db: Session,
    fund_account_id: str = None,
    security_account_id: str = None,
    investor_id: str = None,
) -> AccountAssociation | None:
    """查询账户关联"""
    query = db.query(AccountAssociation)
    
    if fund_account_id:
        query = query.filter(AccountAssociation.fund_account_id == fund_account_id)
    
    if security_account_id:
        query = query.filter(AccountAssociation.security_account_id == security_account_id)
    
    if investor_id:
        query = query.filter(AccountAssociation.investor_id == investor_id)
    
    return query.first()


def check_association_exists(
    db: Session,
    fund_account_id: str,
    security_account_id: str,
) -> bool:
    """检查账户关联是否存在且有效"""
    association = db.query(AccountAssociation).filter(
        and_(
            AccountAssociation.fund_account_id == fund_account_id,
            AccountAssociation.security_account_id == security_account_id,
            AccountAssociation.association_status == AssociationStatus.ACTIVE,
        )
    ).first()
    return association is not None


def update_association_status(
    db: Session,
    association_id: str,
    new_status: AssociationStatus,
) -> bool:
    """更新关联状态"""
    association = db.query(AccountAssociation).filter(
        AccountAssociation.association_id == association_id
    ).first()
    
    if not association:
        return False
    
    association.association_status = new_status
    db.commit()
    return True
