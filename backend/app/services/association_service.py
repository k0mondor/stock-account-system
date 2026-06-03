from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import AccountStatus, AssociationStatus
from app.models.association import AccountAssociation
from app.models.fund_account import FundAccount


def _new_id(prefix: str) -> str:
    return f"{prefix}{uuid4().hex[:18].upper()}"


def get_association(
    db: Session,
    fund_account_id: str | None = None,
    security_account_id: str | None = None,
    investor_id: str | None = None,
) -> AccountAssociation | None:
    """查询账户关联关系。至少提供一个查询条件。只返回当前有效绑定。"""
    query = select(AccountAssociation).where(
        AccountAssociation.association_status == AssociationStatus.ACTIVE.value
    )
    if fund_account_id:
        query = query.where(AccountAssociation.fund_account_id == fund_account_id)
    if security_account_id:
        query = query.where(AccountAssociation.security_account_id == security_account_id)
    if investor_id:
        query = query.where(AccountAssociation.investor_id == investor_id)
    return db.scalars(query).first()


def check_association(
    db: Session,
    fund_account_id: str,
    security_account_id: str,
    operation_type: str,
    investor_id: str | None = None,
) -> dict:
    """账户关联业务校验。判断证券账户与资金账户是否满足一对一绑定。"""
    fund_account = db.get(FundAccount, fund_account_id)
    association = db.scalars(
        select(AccountAssociation).where(
            AccountAssociation.fund_account_id == fund_account_id,
            AccountAssociation.security_account_id == security_account_id,
            AccountAssociation.association_status == AssociationStatus.ACTIVE.value,
        )
    ).first()

    resolved_investor_id = investor_id or (
        association.investor_id if association else (
            fund_account.investor_id if fund_account else "UNKNOWN"
        )
    )

    fund_status = fund_account.account_status if fund_account else "NOT_FOUND"
    sec_status = "NORMAL"
    is_related = association is not None
    is_unique_valid = is_related

    allow_operation = True
    reason = None

    if fund_account is None:
        allow_operation = False
        reason = "资金账户不存在"
    elif fund_account.account_status != AccountStatus.NORMAL.value:
        allow_operation = False
        status_reasons = {
            AccountStatus.FROZEN.value: "资金账户已冻结，不能执行当前业务",
            AccountStatus.LOST.value: "资金账户已挂失，不能执行当前业务",
            AccountStatus.CLOSED.value: "资金账户已注销，不能执行当前业务",
        }
        reason = status_reasons.get(
            fund_account.account_status, f"资金账户状态异常({fund_account.account_status})"
        )
    elif not is_related:
        allow_operation = False
        reason = "资金账户与证券账户未建立绑定关系"
    elif investor_id and association and association.investor_id != investor_id:
        allow_operation = False
        reason = "投资者编号与账户归属不一致"

    return {
        "fund_account_id": fund_account_id,
        "security_account_id": security_account_id,
        "investor_id": resolved_investor_id,
        "is_related": is_related,
        "is_unique_valid": is_unique_valid,
        "allow_operation": allow_operation,
        "fund_account_status": fund_status,
        "security_account_status": sec_status,
        "reason": reason,
    }


def create_association(
    db: Session,
    investor_id: str,
    fund_account_id: str,
    security_account_id: str,
) -> AccountAssociation:
    """创建账户关联。一个资金账户只能绑定一个证券账户。"""
    existing_fund = db.scalars(
        select(AccountAssociation).where(
            AccountAssociation.fund_account_id == fund_account_id,
            AccountAssociation.association_status == AssociationStatus.ACTIVE.value,
        )
    ).first()
    if existing_fund:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"资金账户 {fund_account_id} 已关联证券账户 {existing_fund.security_account_id}",
        )

    existing_sec = db.scalars(
        select(AccountAssociation).where(
            AccountAssociation.security_account_id == security_account_id,
            AccountAssociation.association_status == AssociationStatus.ACTIVE.value,
        )
    ).first()
    if existing_sec:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"证券账户 {security_account_id} 已关联资金账户 {existing_sec.fund_account_id}",
        )

    now = datetime.utcnow()
    association = AccountAssociation(
        association_id=_new_id("ASC"),
        investor_id=investor_id,
        fund_account_id=fund_account_id,
        security_account_id=security_account_id,
        association_status=AssociationStatus.ACTIVE.value,
        associated_at=now,
    )
    db.add(association)
    db.flush()
    return association


def unlink_association(
    db: Session,
    fund_account_id: str | None = None,
    security_account_id: str | None = None,
) -> AccountAssociation:
    """解除账户关联。"""
    query = select(AccountAssociation).where(
        AccountAssociation.association_status == AssociationStatus.ACTIVE.value
    )
    if fund_account_id:
        query = query.where(AccountAssociation.fund_account_id == fund_account_id)
    if security_account_id:
        query = query.where(AccountAssociation.security_account_id == security_account_id)

    association = db.scalars(query).first()
    if not association:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到有效的账户关联关系",
        )

    association.association_status = AssociationStatus.UNLINKED.value
    association.updated_at = datetime.utcnow()
    db.flush()
    return association
