"""账户申请业务逻辑"""

import uuid
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud import application as application_crud
from app.crud import user as user_crud
from app.models import (
    AccountApplication,
    AccountAssociation,
    ApprovalHistory,
    FundAccount,
    InvestorUser,
    SecurityAccount,
)
from app.utils.constants import AssociationStatus
from app.utils.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
)
from app.utils.jwt_utils import get_password_hash

_ACTIVE_APPLICATION_STATUSES = ("PENDING", "APPROVED", "PROCESSING")
_DEFAULT_PASSWORD = "123456"


def _application_to_dict(app: AccountApplication, *, include_contact: bool = True) -> dict:
    data = {
        "application_id": app.application_id,
        "investor_id": app.investor_id,
        "username": app.username,
        "real_name": app.real_name,
        "id_card": app.id_card,
        "status": app.status,
        "fund_account_id": app.fund_account_id,
        "security_account_id": app.security_account_id,
        "approval_reason": app.approval_reason,
        "approval_at": app.approval_at,
        "created_at": app.created_at,
        "updated_at": app.updated_at,
    }
    if include_contact:
        data["phone"] = app.phone
        data["email"] = app.email
    return data


def _ensure_no_existing_investor(db: Session, username: str, id_card: str) -> None:
    if user_crud.get_user_by_username(db, username):
        raise ConflictException(f"用户名已被使用: {username}")
    if user_crud.get_user_by_id_card(db, id_card):
        raise ConflictException(f"身份证已被使用: {id_card}")


def _ensure_application_available(
    db: Session,
    username: str,
    id_card: str,
) -> AccountApplication | None:
    """检查是否已有进行中的申请，返回可复用的已拒绝申请（如有）。"""
    by_username = application_crud.get_application_by_username(db, username)
    by_id_card = application_crud.get_application_by_id_card(db, id_card)

    for existing in (by_username, by_id_card):
        if not existing:
            continue
        if existing.status in _ACTIVE_APPLICATION_STATUSES:
            if existing.username == username:
                raise ConflictException(f"用户名已被使用: {username}")
            raise ConflictException(f"身份证已被使用: {id_card}")
        if existing.status == "REJECTED":
            if by_username and by_id_card and by_username.application_id != by_id_card.application_id:
                raise ConflictException("用户名与身份证分属不同历史申请，无法提交")
            return existing

    if by_username and by_username.status == "REJECTED":
        return by_username
    if by_id_card and by_id_card.status == "REJECTED":
        return by_id_card
    return None


def submit_application(
    db: Session,
    username: str,
    real_name: str,
    id_card: str,
    phone: str,
    email: str,
) -> dict:
    """提交开户申请"""
    _ensure_no_existing_investor(db, username, id_card)
    reusable = _ensure_application_available(db, username, id_card)

    try:
        if reusable:
            application = application_crud.resubmit_application(
                db,
                reusable,
                real_name=real_name,
                phone=phone,
                email=email,
            )
            application_id = application.application_id
            remark = "被拒绝后重新提交申请"
        else:
            application_id = f"APP{uuid.uuid4().hex[:18].upper()}"
            application = application_crud.create_application(
                db=db,
                application_id=application_id,
                username=username,
                real_name=real_name,
                id_card=id_card,
                phone=phone,
                email=email,
            )
            remark = "申请提交"

        history_id = f"HIS{uuid.uuid4().hex[:18].upper()}"
        application_crud.create_approval_history(
            db=db,
            history_id=history_id,
            application_id=application_id,
            action="SUBMIT",
            action_by=username,
            action_by_name=real_name,
            old_status="REJECTED" if reusable else None,
            new_status="PENDING",
            remark=remark,
        )
        return _application_to_dict(application)
    except IntegrityError:
        db.rollback()
        raise ConflictException(f"用户名或身份证已被使用: {username}")


def query_application(
    db: Session,
    application_id: str = None,
    username: str = None,
    id_card: str = None,
    status: str = None,
) -> list[dict]:
    """查询申请"""
    applications = application_crud.query_applications(
        db=db,
        application_id=application_id,
        username=username,
        id_card=id_card,
        status=status,
    )
    return [_application_to_dict(app) for app in applications]


def approve_application(
    db: Session,
    application_id: str,
    approver_id: str,
    approver_name: str,
    approval_reason: str,
) -> dict:
    """审批通过申请并创建证券账户、资金账户及一对一绑定（单事务）。"""
    application = application_crud.get_application(db, application_id)
    if not application:
        raise NotFoundException(f"申请不存在: {application_id}")

    if application.status != "PENDING":
        raise BadRequestException(f"申请状态异常: {application.status}")

    _ensure_no_existing_investor(db, application.username, application.id_card)

    investor_id = f"INV{uuid.uuid4().hex[:18].upper()}"
    fund_account_id = f"FUND{uuid.uuid4().hex[:14].upper()}"
    security_account_id = f"SEC{uuid.uuid4().hex[:15].upper()}"
    association_id = f"ASC{uuid.uuid4().hex[:18].upper()}"
    history_id = f"HIS{uuid.uuid4().hex[:18].upper()}"
    password_hash = get_password_hash(_DEFAULT_PASSWORD)

    try:
        db.add(
            InvestorUser(
                investor_id=investor_id,
                username=application.username,
                real_name=application.real_name,
                id_card=application.id_card,
                phone=application.phone,
                email=application.email,
                trade_password_hash=password_hash,
                withdraw_password_hash=password_hash,
            )
        )
        db.add(
            FundAccount(
                fund_account_id=fund_account_id,
                investor_id=investor_id,
                bank_card_no=None,
                available_amount=Decimal("0.00"),
                frozen_amount=Decimal("0.00"),
                total_amount=Decimal("0.00"),
            )
        )
        db.add(
            SecurityAccount(
                security_account_id=security_account_id,
                investor_id=investor_id,
            )
        )
        db.add(
            AccountAssociation(
                association_id=association_id,
                investor_id=investor_id,
                fund_account_id=fund_account_id,
                security_account_id=security_account_id,
                association_status=AssociationStatus.ACTIVE,
                remark="开户审批通过后自动创建",
            )
        )

        application.status = "APPROVED"
        application.investor_id = investor_id
        application.fund_account_id = fund_account_id
        application.security_account_id = security_account_id
        application.approver_id = approver_id
        application.approver_name = approver_name
        application.approval_reason = approval_reason
        application_crud.set_application_approval_time(application)

        db.add(
            ApprovalHistory(
                history_id=history_id,
                application_id=application_id,
                action="APPROVE",
                action_by=approver_id,
                action_by_name=approver_name,
                old_status="PENDING",
                new_status="APPROVED",
                remark=approval_reason,
            )
        )

        db.commit()
        db.refresh(application)
    except IntegrityError as exc:
        db.rollback()
        raise ConflictException("审批通过失败：用户名或身份证已存在投资者账户") from exc
    except Exception as exc:
        db.rollback()
        raise BadRequestException(f"审批通过失败: {exc}") from exc

    return {
        "application_id": application.application_id,
        "investor_id": application.investor_id,
        "status": application.status,
        "fund_account_id": application.fund_account_id,
        "security_account_id": application.security_account_id,
        "approval_reason": application.approval_reason,
        "approval_at": application.approval_at,
    }


def reject_application(
    db: Session,
    application_id: str,
    approver_id: str,
    approver_name: str,
    reject_reason: str,
) -> dict:
    """拒绝申请"""
    application = application_crud.get_application(db, application_id)
    if not application:
        raise NotFoundException(f"申请不存在: {application_id}")

    if application.status != "PENDING":
        raise BadRequestException(f"申请状态异常: {application.status}")

    try:
        updated_app = application_crud.update_application_approval(
            db=db,
            application_id=application_id,
            status="REJECTED",
            approver_id=approver_id,
            approver_name=approver_name,
            approval_reason=reject_reason,
        )

        history_id = f"HIS{uuid.uuid4().hex[:18].upper()}"
        application_crud.create_approval_history(
            db=db,
            history_id=history_id,
            application_id=application_id,
            action="REJECT",
            action_by=approver_id,
            action_by_name=approver_name,
            old_status="PENDING",
            new_status="REJECTED",
            remark=reject_reason,
        )

        return {
            "application_id": updated_app.application_id,
            "status": updated_app.status,
            "approval_reason": updated_app.approval_reason,
            "approval_at": updated_app.approval_at,
        }
    except Exception as exc:
        db.rollback()
        raise BadRequestException(f"拒绝申请失败: {exc}") from exc


def get_approval_history(db: Session, application_id: str) -> dict:
    """获取审批历史"""
    application = application_crud.get_application(db, application_id)
    if not application:
        raise NotFoundException(f"申请不存在: {application_id}")

    histories = application_crud.get_approval_histories(db, application_id)
    result = []
    for h in histories:
        result.append({
            "history_id": h.history_id,
            "action": h.action,
            "action_by": h.action_by,
            "action_by_name": h.action_by_name,
            "old_status": h.old_status,
            "new_status": h.new_status,
            "remark": h.remark,
            "created_at": h.created_at,
        })

    return {
        "application_id": application_id,
        "histories": result,
    }
