"""资金账户模型"""

from decimal import Decimal
from sqlalchemy import Column, String, DateTime, Boolean, Numeric, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.sql import func
from app.database import Base
from app.utils.constants import AccountStatus


class FundAccount(Base):
    """资金账户表"""
    __tablename__ = "fund_accounts"
    __table_args__ = (
        Index('idx_investor_id', 'investor_id'),
        Index('idx_account_status', 'status'),
    )
    
    # 主键
    fund_account_id = Column(String(50), primary_key=True, index=True)
    
    # 关联信息
    investor_id = Column(String(50), index=True, nullable=False)
    bank_card_no = Column(String(50), nullable=True)  # 银行卡号，可脱敏存储
    
    # 资金信息
    available_amount = Column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)  # 可用资金
    frozen_amount = Column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)  # 冻结资金
    total_amount = Column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)  # 总资金
    
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
        return f"<FundAccount(fund_account_id={self.fund_account_id}, investor_id={self.investor_id})>"


class FundFreeze(Base):
    """资金冻结记录表"""
    __tablename__ = "fund_freezes"
    __table_args__ = (
        Index('idx_fund_account_order', 'fund_account_id', 'order_id'),
    )
    
    # 主键
    freeze_id = Column(String(50), primary_key=True, index=True)
    
    # 关联信息
    fund_account_id = Column(String(50), ForeignKey('fund_accounts.fund_account_id'), index=True, nullable=False)
    order_id = Column(String(50), index=True, nullable=False)
    message_id = Column(String(50), index=True)
    
    # 冻结信息
    freeze_amount = Column(Numeric(18, 2), nullable=False)
    freeze_reason = Column(String(100), nullable=False)  # SELL_ORDER/TRADE_ORDER等
    
    # 状态
    is_released = Column(Boolean, default=False, index=True)
    release_reason = Column(String(100))
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    released_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<FundFreeze(freeze_id={self.freeze_id}, freeze_amount={self.freeze_amount})>"


class FundSettlement(Base):
    """资金结算记录表"""
    __tablename__ = "fund_settlements"
    __table_args__ = (
        Index('idx_fund_account_message', 'fund_account_id', 'message_id'),
    )
    
    # 主键
    settlement_id = Column(String(50), primary_key=True, index=True)
    
    # 关联信息
    fund_account_id = Column(String(50), ForeignKey('fund_accounts.fund_account_id'), index=True, nullable=False)
    message_id = Column(String(50), unique=True, index=True, nullable=False)
    order_id = Column(String(50), index=True)
    trade_id = Column(String(50), index=True)
    
    # 结算信息
    settlement_type = Column(String(50), nullable=False)  # DEDUCT/INCREASE
    settlement_amount = Column(Numeric(18, 2), nullable=False)
    settlement_reason = Column(String(100), nullable=False)  # TRADE_FILLED/TRADE_CANCELLED等
    
    # 结果
    available_amount_after = Column(Numeric(18, 2), nullable=False)
    frozen_amount_after = Column(Numeric(18, 2), nullable=False)
    total_amount_after = Column(Numeric(18, 2), nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<FundSettlement(settlement_id={self.settlement_id}, amount={self.settlement_amount})>"
