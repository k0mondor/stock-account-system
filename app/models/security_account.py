"""证券账户和持仓模型"""

from sqlalchemy import Column, String, DateTime, Boolean, Integer, Numeric, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.sql import func
from app.database import Base
from app.utils.constants import AccountStatus


class SecurityAccount(Base):
    """证券账户表"""
    __tablename__ = "security_accounts"
    __table_args__ = (
        Index('idx_security_investor_id', 'investor_id'),
        Index('idx_security_account_status', 'status'),
    )
    
    # 主键
    security_account_id = Column(String(50), primary_key=True, index=True)
    
    # 关联信息
    investor_id = Column(String(50), index=True, nullable=False)
    
    # 状态
    status = Column(
        SQLEnum(AccountStatus),
        default=AccountStatus.NORMAL,
        index=True,
        nullable=False
    )
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<SecurityAccount(security_account_id={self.security_account_id}, investor_id={self.investor_id})>"


class SecurityPosition(Base):
    """证券持仓表"""
    __tablename__ = "security_positions"
    __table_args__ = (
        Index('idx_security_account_stock', 'security_account_id', 'stock_code'),
    )
    
    # 主键
    position_id = Column(String(50), primary_key=True, index=True)
    
    # 关联信息
    security_account_id = Column(
        String(50),
        ForeignKey('security_accounts.security_account_id'),
        index=True,
        nullable=False
    )
    investor_id = Column(String(50), index=True, nullable=False)
    stock_code = Column(String(20), index=True, nullable=False)
    stock_name = Column(String(100))
    
    # 持仓数据
    total_quantity = Column(Integer, default=0, nullable=False)  # 总持仓
    available_quantity = Column(Integer, default=0, nullable=False)  # 可卖数量
    frozen_quantity = Column(Integer, default=0, nullable=False)  # 冻结数量
    cost_price = Column(Numeric(18, 4))  # 持仓成本
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<SecurityPosition(position_id={self.position_id}, stock_code={self.stock_code})>"


class PositionFreeze(Base):
    """证券持仓冻结记录表"""
    __tablename__ = "position_freezes"
    __table_args__ = (
        Index('idx_security_account_order', 'security_account_id', 'order_id'),
    )
    
    # 主键
    freeze_id = Column(String(50), primary_key=True, index=True)
    
    # 关联信息
    security_account_id = Column(String(50), index=True, nullable=False)
    position_id = Column(String(50), ForeignKey('security_positions.position_id'), index=True, nullable=False)
    order_id = Column(String(50), index=True, nullable=False)
    message_id = Column(String(50), index=True)
    stock_code = Column(String(20), nullable=False)
    
    # 冻结信息
    freeze_quantity = Column(Integer, nullable=False)
    freeze_reason = Column(String(100), nullable=False)  # SELL_ORDER等
    
    # 状态
    is_released = Column(Boolean, default=False, index=True)
    release_reason = Column(String(100))
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    released_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<PositionFreeze(freeze_id={self.freeze_id}, freeze_quantity={self.freeze_quantity})>"


class PositionSettlement(Base):
    """证券持仓结算记录表"""
    __tablename__ = "position_settlements"
    __table_args__ = (
        Index('idx_security_account_message', 'security_account_id', 'message_id'),
    )
    
    # 主键
    settlement_id = Column(String(50), primary_key=True, index=True)
    
    # 关联信息
    security_account_id = Column(String(50), index=True, nullable=False)
    position_id = Column(String(50), ForeignKey('security_positions.position_id'), index=True, nullable=False)
    message_id = Column(String(50), unique=True, index=True, nullable=False)
    order_id = Column(String(50), index=True)
    trade_id = Column(String(50), index=True)
    stock_code = Column(String(20), nullable=False)
    
    # 结算信息
    settlement_type = Column(String(50), nullable=False)  # DEDUCT/INCREASE
    settlement_quantity = Column(Integer, nullable=False)
    settlement_reason = Column(String(100), nullable=False)  # TRADE_FILLED/TRADE_CANCELLED等
    
    # 结果
    total_quantity_after = Column(Integer, nullable=False)
    available_quantity_after = Column(Integer, nullable=False)
    frozen_quantity_after = Column(Integer, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<PositionSettlement(settlement_id={self.settlement_id}, quantity={self.settlement_quantity})>"
