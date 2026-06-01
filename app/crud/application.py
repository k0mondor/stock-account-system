"""账户申请数据访问层"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session
from app.models import AccountApplication, ApprovalHistory


def set_application_approval_time(application: AccountApplication) -> None:
    """设置审批时间为当前 UTC 时间"""
    application.approval_at = datetime.now(timezone.utc)


def create_application(
    db: Session,
    application_id: str,
    username: str,
    real_name: str,
    id_card: str,
    phone: str,
    email: str,
) -> AccountApplication:
    """创建账户申请"""
    application = AccountApplication(
        application_id=application_id,
        username=username,
        real_name=real_name,
        id_card=id_card,
        phone=phone,
        email=email,
        status="PENDING",
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def get_application(db: Session, application_id: str) -> AccountApplication | None:
    """获取申请详情"""
    return db.query(AccountApplication).filter(
        AccountApplication.application_id == application_id
    ).first()


def get_application_by_id_card(db: Session, id_card: str) -> AccountApplication | None:
    """通过身份证号获取申请"""
    return db.query(AccountApplication).filter(
        AccountApplication.id_card == id_card
    ).first()


def get_application_by_username(db: Session, username: str) -> AccountApplication | None:
    """通过用户名获取申请"""
    return db.query(AccountApplication).filter(
        AccountApplication.username == username
    ).first()


def query_applications(
    db: Session,
    application_id: str = None,
    username: str = None,
    id_card: str = None,
    status: str = None,
) -> list[AccountApplication]:
    """查询申请列表"""
    query = db.query(AccountApplication)
    
    if application_id:
        query = query.filter(AccountApplication.application_id == application_id)
    
    if username:
        query = query.filter(AccountApplication.username.like(f"%{username}%"))
    
    if id_card:
        query = query.filter(AccountApplication.id_card == id_card)
    
    if status:
        query = query.filter(AccountApplication.status == status)
    
    return query.order_by(AccountApplication.created_at.desc()).all()


def resubmit_application(
    db: Session,
    application: AccountApplication,
    real_name: str,
    phone: str,
    email: str,
) -> AccountApplication:
    """被拒绝的申请重新提交"""
    application.real_name = real_name
    application.phone = phone
    application.email = email
    application.status = "PENDING"
    application.investor_id = None
    application.fund_account_id = None
    application.security_account_id = None
    application.approver_id = None
    application.approver_name = None
    application.approval_reason = None
    application.approval_at = None
    db.commit()
    db.refresh(application)
    return application


def update_application_approval(
    db: Session,
    application_id: str,
    status: str,
    investor_id: str = None,
    fund_account_id: str = None,
    security_account_id: str = None,
    approver_id: str = None,
    approver_name: str = None,
    approval_reason: str = None,
) -> AccountApplication | None:
    """更新申请审批结果"""
    application = get_application(db, application_id)
    if not application:
        return None
    
    application.status = status
    
    if investor_id:
        application.investor_id = investor_id
    
    if fund_account_id:
        application.fund_account_id = fund_account_id
    
    if security_account_id:
        application.security_account_id = security_account_id
    
    if approver_id:
        application.approver_id = approver_id
    
    if approver_name:
        application.approver_name = approver_name
    
    if approval_reason:
        application.approval_reason = approval_reason
    
    set_application_approval_time(application)
    
    db.commit()
    db.refresh(application)
    return application


def create_approval_history(
    db: Session,
    history_id: str,
    application_id: str,
    action: str,
    action_by: str,
    action_by_name: str = None,
    old_status: str = None,
    new_status: str = None,
    remark: str = None,
) -> ApprovalHistory:
    """创建审批历史记录"""
    history = ApprovalHistory(
        history_id=history_id,
        application_id=application_id,
        action=action,
        action_by=action_by,
        action_by_name=action_by_name,
        old_status=old_status,
        new_status=new_status,
        remark=remark,
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


def get_approval_histories(
    db: Session,
    application_id: str,
) -> list[ApprovalHistory]:
    """获取申请的审批历史"""
    return db.query(ApprovalHistory).filter(
        ApprovalHistory.application_id == application_id
    ).order_by(ApprovalHistory.created_at.asc()).all()
