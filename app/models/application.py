"""账户申请模型"""

from sqlalchemy import Column, String, DateTime, Boolean, Enum as SQLEnum, Text, Index
from sqlalchemy.sql import func
from app.database import Base


class ApplicationStatus(str):
    """申请状态"""
    PENDING = "PENDING"  # 待审批
    APPROVED = "APPROVED"  # 已批准
    REJECTED = "REJECTED"  # 已拒绝
    PROCESSING = "PROCESSING"  # 处理中


class AccountApplication(Base):
    """账户开户申请表"""
    __tablename__ = "account_applications"
    __table_args__ = (
        Index('idx_app_investor_id', 'investor_id'),
        Index('idx_app_status', 'status'),
        Index('idx_app_created_at', 'created_at'),
    )
    
    # 主键
    application_id = Column(String(50), primary_key=True, index=True)
    
    # 投资者信息
    investor_id = Column(String(50), unique=True, index=True, nullable=True)  # 审批后才有
    username = Column(String(100), unique=True, index=True, nullable=False)
    real_name = Column(String(100), nullable=False)
    id_card = Column(String(20), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    
    # 账户信息
    fund_account_id = Column(String(50), nullable=True)  # 审批通过后创建
    security_account_id = Column(String(50), nullable=True)  # 审批通过后创建
    
    # 申请状态
    status = Column(
        String(20),
        default=ApplicationStatus.PENDING,
        index=True,
        nullable=False
    )
    
    # 审批信息
    approver_id = Column(String(50))  # 审批人编号
    approver_name = Column(String(100))  # 审批人姓名
    approval_reason = Column(Text)  # 审批意见
    approval_at = Column(DateTime(timezone=True))  # 审批时间
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<AccountApplication(application_id={self.application_id}, username={self.username}, status={self.status})>"


class ApprovalHistory(Base):
    """审批历史记录表"""
    __tablename__ = "approval_histories"
    __table_args__ = (
        Index('idx_approval_application_id', 'application_id'),
        Index('idx_approval_created_at', 'created_at'),
    )
    
    # 主键
    history_id = Column(String(50), primary_key=True, index=True)
    
    # 关联信息
    application_id = Column(String(50), index=True, nullable=False)
    
    # 审批信息
    action = Column(String(50), nullable=False)  # SUBMIT/REVIEW/APPROVE/REJECT
    action_by = Column(String(50), nullable=False)  # 操作人（投资者或审批人）
    action_by_name = Column(String(100))  # 操作人名称
    
    # 状态变更
    old_status = Column(String(20))
    new_status = Column(String(20))
    
    # 备注
    remark = Column(Text)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<ApprovalHistory(history_id={self.history_id}, action={self.action})>"
