"""账户关联模型"""

from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, Index
from sqlalchemy.sql import func
from app.database import Base
from app.utils.constants import AssociationStatus


class AccountAssociation(Base):
    """账户关联表（证券账户与资金账户的一对一绑定）"""
    __tablename__ = "account_associations"
    __table_args__ = (
        Index('idx_fund_account', 'fund_account_id'),
        Index('idx_security_account', 'security_account_id'),
        Index('idx_investor', 'investor_id'),
        Index('idx_association_status', 'association_status'),
    )
    
    # 主键
    association_id = Column(String(50), primary_key=True, index=True)
    
    # 关联信息
    investor_id = Column(String(50), index=True, nullable=False)
    fund_account_id = Column(String(50), unique=True, index=True, nullable=False)
    security_account_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # 关联状态
    association_status = Column(
        SQLEnum(AssociationStatus),
        default=AssociationStatus.ACTIVE,
        index=True,
        nullable=False
    )
    
    # 备注
    remark = Column(String(500))
    
    # 时间戳
    associated_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<AccountAssociation(association_id={self.association_id}, fund={self.fund_account_id}, security={self.security_account_id})>"
