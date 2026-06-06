from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.account_rules import allowed_statuses, status_rejection_reason
from app.core.enums import AccountStatus, AssociationStatus
from app.core.time import utc_now
from app.models.association import AccountAssociation
from app.models.fund_account import FundAccount
from app.models.security_account import SecuritiesAccount
from app.services.operation_log_service import add_operation_log


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


def list_association_history(
    db: Session,
    *,
    fund_account_id: str | None = None,
    security_account_id: str | None = None,
    investor_id: str | None = None,
) -> list[AccountAssociation]:
    """查询当前及已解除的账户关联历史。"""
    query = select(AccountAssociation)
    if fund_account_id:
        query = query.where(AccountAssociation.fund_account_id == fund_account_id)
    if security_account_id:
        query = query.where(
            AccountAssociation.security_account_id == security_account_id
        )
    if investor_id:
        query = query.where(AccountAssociation.investor_id == investor_id)
    return list(
        db.scalars(
            query.order_by(
                AccountAssociation.associated_at.desc(),
                AccountAssociation.created_at.desc(),
            )
        ).all()
    )


def check_association(
    db: Session,
    fund_account_id: str,
    security_account_id: str,
    operation_type: str,
    investor_id: str | None = None,
) -> dict:
    """账户关联业务校验。判断证券账户与资金账户是否满足一对一绑定。"""
    fund_account = db.get(FundAccount, fund_account_id)
    security_account = db.get(SecuritiesAccount, security_account_id)
    operation_statuses = allowed_statuses(operation_type)
    associations = list(db.scalars(
        select(AccountAssociation).where(
            AccountAssociation.fund_account_id == fund_account_id,
            AccountAssociation.security_account_id == security_account_id,
            AccountAssociation.association_status == AssociationStatus.ACTIVE.value,
        )
    ).all())

    resolved_investor_id = investor_id or (
        associations[0].investor_id if associations else (
            fund_account.investor_id if fund_account else "UNKNOWN"
        )
    )

    fund_status = fund_account.account_status if fund_account else "NOT_FOUND"
    sec_status = (
        security_account.account_status if security_account else "NOT_FOUND"
    )
    is_related = len(associations) > 0
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
    is_unique_valid = (
        len(associations) == 1
        and active_fund_count == 1
        and active_security_count == 1
    )

    allow_operation = True
    reason = None

    if fund_account is None:
        allow_operation = False
        reason = "资金账户不存在"
    elif security_account is None:
        allow_operation = False
        reason = "证券账户不存在"
    elif operation_statuses is None:
        allow_operation = False
        reason = f"不支持的业务类型: {operation_type}"
    elif fund_account.account_status not in operation_statuses:
        allow_operation = False
        reason = status_rejection_reason(
            "资金账户", fund_account.account_status
        )
    elif security_account.account_status not in operation_statuses:
        allow_operation = False
        reason = status_rejection_reason(
            "证券账户", security_account.account_status
        )
    elif not is_related:
        allow_operation = False
        reason = "资金账户与证券账户未建立绑定关系"
    elif not is_unique_valid:
        allow_operation = False
        reason = "账户关联不满足一对一唯一有效约束"
    elif (
        fund_account.investor_id != security_account.investor_id
        or associations[0].investor_id != fund_account.investor_id
    ):
        allow_operation = False
        reason = "账户关联中的投资者归属不一致"
    elif investor_id and associations[0].investor_id != investor_id:
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


def require_active_association_for_fund(
    db: Session,
    *,
    fund_account_id: str,
    operation_type: str,
) -> AccountAssociation:
    associations = list(
        db.scalars(
            select(AccountAssociation).where(
                AccountAssociation.fund_account_id == fund_account_id,
                AccountAssociation.association_status
                == AssociationStatus.ACTIVE.value,
            )
        ).all()
    )
    if len(associations) != 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="资金账户不存在唯一有效的证券账户绑定",
        )
    association = associations[0]
    result = check_association(
        db,
        fund_account_id=fund_account_id,
        security_account_id=association.security_account_id,
        operation_type=operation_type,
        investor_id=association.investor_id,
    )
    if not result["allow_operation"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=result["reason"] or "账户关联校验未通过",
        )
    return association


def require_active_association_for_security(
    db: Session,
    *,
    security_account_id: str,
    operation_type: str,
) -> AccountAssociation:
    associations = list(
        db.scalars(
            select(AccountAssociation).where(
                AccountAssociation.security_account_id == security_account_id,
                AccountAssociation.association_status
                == AssociationStatus.ACTIVE.value,
            )
        ).all()
    )
    if len(associations) != 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="证券账户不存在唯一有效的资金账户绑定",
        )
    association = associations[0]
    result = check_association(
        db,
        fund_account_id=association.fund_account_id,
        security_account_id=security_account_id,
        operation_type=operation_type,
        investor_id=association.investor_id,
    )
    if not result["allow_operation"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=result["reason"] or "账户关联校验未通过",
        )
    return association


def create_association(
    db: Session,
    investor_id: str,
    fund_account_id: str,
    security_account_id: str,
    *,
    log_operation: bool = True,
) -> AccountAssociation:
    """创建账户关联。一个资金账户只能绑定一个证券账户。"""
    fund_account = db.scalar(
        select(FundAccount)
        .where(FundAccount.fund_account_id == fund_account_id)
        .with_for_update()
    )
    security_account = db.scalar(
        select(SecuritiesAccount)
        .where(SecuritiesAccount.security_account_id == security_account_id)
        .with_for_update()
    )
    if not fund_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"资金账户 {fund_account_id} 不存在",
        )
    if not security_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"证券账户 {security_account_id} 不存在",
        )
    if fund_account.account_status != AccountStatus.NORMAL.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="资金账户状态异常，无法建立关联",
        )
    if security_account.account_status != AccountStatus.NORMAL.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="证券账户状态异常，无法建立关联",
        )
    if (
        fund_account.investor_id != investor_id
        or security_account.investor_id != investor_id
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="投资者编号与账户归属不一致",
        )

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

    now = utc_now()
    association = AccountAssociation(
        association_id=_new_id("ASC"),
        investor_id=investor_id,
        fund_account_id=fund_account_id,
        security_account_id=security_account_id,
        association_status=AssociationStatus.ACTIVE.value,
        associated_at=now,
    )
    db.add(association)
    if log_operation:
        add_operation_log(
            db,
            operator_id="SYSTEM",
            operator_name="系统",
            operation_type="LINK_ASSOCIATION",
            target_type="ASSOCIATION",
            target_id=association.association_id,
            operation_detail=(
                f"建立资金账户 {fund_account_id} 与证券账户 "
                f"{security_account_id} 的一对一绑定"
            ),
        )
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

    associations = list(db.scalars(query.with_for_update()).all())
    if not associations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到有效的账户关联关系",
        )

    if len(associations) > 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="存在多个有效关联关系，请先修复关联数据",
        )

    association = associations[0]
    association.association_status = AssociationStatus.UNLINKED.value
    now = utc_now()
    association.disassociated_at = now
    association.updated_at = now
    add_operation_log(
        db,
        operator_id="SYSTEM",
        operator_name="系统",
        operation_type="UNLINK_ASSOCIATION",
        target_type="ASSOCIATION",
        target_id=association.association_id,
        operation_detail="解除当前有效绑定关系并保留历史记录",
    )
    db.flush()
    return association
