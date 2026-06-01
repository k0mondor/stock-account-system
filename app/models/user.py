"""投资者用户模型"""

from sqlalchemy import Column, String, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base
from app.utils.constants import PasswordType


class InvestorUser(Base):
    """投资者用户表"""
    __tablename__ = "investor_users"
    
    # 主键
    investor_id = Column(String(50), primary_key=True, index=True)
    
    # 基本信息
    username = Column(String(100), unique=True, index=True, nullable=False)
    real_name = Column(String(100), nullable=False)
    id_card = Column(String(20), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True)
    
    # 安全信息
    trade_password_hash = Column(String(255), nullable=False)  # 交易密码哈希
    withdraw_password_hash = Column(String(255), nullable=False)  # 取款密码哈希
    
    # 状态
    is_active = Column(Boolean, default=True, index=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<InvestorUser(investor_id={self.investor_id}, username={self.username})>"


class OperationLog(Base):
    """操作日志表"""
    __tablename__ = "operation_logs"
    
    # 主键
    log_id = Column(String(50), primary_key=True, index=True)
    
    # 关联信息
    investor_id = Column(String(50), index=True, nullable=False)
    operator = Column(String(100), nullable=False)  # 操作者标识
    
    # 操作信息
    operation_type = Column(String(100), index=True, nullable=False)
    object_type = Column(String(100), nullable=False)  # 操作对象类型
    object_id = Column(String(100), nullable=False)
    
    # 操作详情
    action = Column(String(50), nullable=False)  # 操作行为：CREATE/UPDATE/DELETE/READ
    old_value = Column(String(1000))  # 变更前值
    new_value = Column(String(1000))  # 变更后值
    description = Column(String(500))  # 操作描述
    
    # 结果
    is_success = Column(Boolean, default=True)
    error_message = Column(String(500))
    
    # 元数据
    request_id = Column(String(100), index=True)
    ip_address = Column(String(50))
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<OperationLog(log_id={self.log_id}, operation_type={self.operation_type})>"
