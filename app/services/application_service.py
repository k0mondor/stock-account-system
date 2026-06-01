"""账户申请业务逻辑"""

import uuid
from sqlalchemy.orm import Session
from app.crud import application as application_crud
from app.crud import user as user_crud
from app.crud import fund_account as fund_account_crud
from app.crud import security_account as security_account_crud
from app.crud import association as association_crud
from app.utils.jwt_utils import get_password_hash
from app.utils.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
)
from decimal import Decimal


def submit_application(
    db: Session,
    username: str,
    real_name: str,
    id_card: str,
    phone: str,
    email: str,
) -> dict:
    """提交开户申请"""
    
    # 检查用户名是否已存在
    existing_app = application_crud.get_application_by_username(db, username)
    if existing_app and existing_app.status in ["APPROVED", "PROCESSING"]:
        raise ConflictException(f"用户名已被使用: {username}")
    
    # 检查身份证是否已存在
    existing_app = application_crud.get_application_by_id_card(db, id_card)
    if existing_app and existing_app.status in ["APPROVED", "PROCESSING"]:
        raise ConflictException(f"身份证已被使用: {id_card}")
    
    # 创建申请
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
    
    # 创建申请历史
    history_id = f"HIS{uuid.uuid4().hex[:18].upper()}"
    application_crud.create_approval_history(
        db=db,
        history_id=history_id,
        application_id=application_id,
        action="SUBMIT",
        action_by=username,
        action_by_name=real_name,
        old_status=None,
        new_status="PENDING",
        remark="申请提交",
    )
    
    return {
        "application_id": application.application_id,
        "username": application.username,
        "real_name": application.real_name,
        "id_card": application.id_card,
        "phone": application.phone,
        "email": application.email,
        "status": application.status,
        "created_at": application.created_at,
    }


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
    
    result = []
    for app in applications:
        result.append({
            "application_id": app.application_id,
            "investor_id": app.investor_id,
            "username": app.username,
            "real_name": app.real_name,
            "id_card": app.id_card,
            "phone": app.phone,
            "email": app.email,
            "status": app.status,
            "fund_account_id": app.fund_account_id,
            "security_account_id": app.security_account_id,
            "approval_reason": app.approval_reason,
            "approval_at": app.approval_at,
            "created_at": app.created_at,
            "updated_at": app.updated_at,
        })
    
    return result


def approve_application(
    db: Session,
    application_id: str,
    approver_id: str,
    approver_name: str,
    approval_reason: str,
) -> dict:
    """审批通过申请并创建账户"""
    
    # 获取申请
    application = application_crud.get_application(db, application_id)
    if not application:
        raise NotFoundException(f"申请不存在: {application_id}")
    
    if application.status != "PENDING":
        raise BadRequestException(f"申请状态异常: {application.status}")
    
    try:
        # 生成投资者ID
        investor_id = f"INV{uuid.uuid4().hex[:18].upper()}"
        
        # 创建投资者用户（使用默认密码）
        default_password = "123456"  # 用户需要登录后修改
        user = user_crud.create_user(
            db=db,
            investor_id=investor_id,
            username=application.username,
            real_name=application.real_name,
            id_card=application.id_card,
            phone=application.phone,
            email=application.email,
            trade_password=default_password,
            withdraw_password=default_password,
        )
        
        # 生成账户ID
        fund_account_id = f"FUND{uuid.uuid4().hex[:14].upper()}"
        security_account_id = f"SEC{uuid.uuid4().hex[:15].upper()}"
        
        # 创建资金账户
        fund_account = fund_account_crud.create_fund_account(
            db=db,
            fund_account_id=fund_account_id,
            investor_id=investor_id,
            bank_card_no=None,
            initial_amount=Decimal("0.00"),
        )
        
        # 创建证券账户
        security_account = security_account_crud.create_security_account(
            db=db,
            security_account_id=security_account_id,
            investor_id=investor_id,
        )
        
        # 建立账户关联（一对一绑定）
        association_id = f"ASC{uuid.uuid4().hex[:18].upper()}"
        association = association_crud.create_association(
            db=db,
            association_id=association_id,
            investor_id=investor_id,
            fund_account_id=fund_account_id,
            security_account_id=security_account_id,
            remark="开户审批通过后自动创建",
        )
        
        # 更新申请状态为已批准
        updated_app = application_crud.update_application_approval(
            db=db,
            application_id=application_id,
            status="APPROVED",
            investor_id=investor_id,
            fund_account_id=fund_account_id,
            security_account_id=security_account_id,
            approver_id=approver_id,
            approver_name=approver_name,
            approval_reason=approval_reason,
        )
        
        # 创建审批历史
        history_id = f"HIS{uuid.uuid4().hex[:18].upper()}"
        application_crud.create_approval_history(
            db=db,
            history_id=history_id,
            application_id=application_id,
            action="APPROVE",
            action_by=approver_id,
            action_by_name=approver_name,
            old_status="PENDING",
            new_status="APPROVED",
            remark=approval_reason,
        )
        
        return {
            "application_id": updated_app.application_id,
            "investor_id": updated_app.investor_id,
            "status": updated_app.status,
            "fund_account_id": updated_app.fund_account_id,
            "security_account_id": updated_app.security_account_id,
            "approval_reason": updated_app.approval_reason,
            "approval_at": updated_app.approval_at,
        }
    
    except Exception as e:
        db.rollback()
        raise Exception(f"审批通过失败: {str(e)}")


def reject_application(
    db: Session,
    application_id: str,
    approver_id: str,
    approver_name: str,
    reject_reason: str,
) -> dict:
    """拒绝申请"""
    
    # 获取申请
    application = application_crud.get_application(db, application_id)
    if not application:
        raise NotFoundException(f"申请不存在: {application_id}")
    
    if application.status != "PENDING":
        raise BadRequestException(f"申请状态异常: {application.status}")
    
    try:
        # 更新申请状态为已拒绝
        updated_app = application_crud.update_application_approval(
            db=db,
            application_id=application_id,
            status="REJECTED",
            approver_id=approver_id,
            approver_name=approver_name,
            approval_reason=reject_reason,
        )
        
        # 创建审批历史
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
    
    except Exception as e:
        db.rollback()
        raise Exception(f"拒绝申请失败: {str(e)}")


def get_approval_history(db: Session, application_id: str) -> dict:
    """获取审批历史"""
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
