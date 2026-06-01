from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import AccountStatus
from app.db.session import Base


class FundAccount(Base):
    """资金账户表"""
    __tablename__ = "fund_accounts"

    # 资金账户号 (主键)
    fund_account_id: Mapped[str] = mapped_column(String(32), primary_key=True, index=True)
    # 投资者编号
    investor_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    # 绑定的银行卡号
    bank_card_number: Mapped[str] = mapped_column(String(32), nullable=False)
    # 交易密码 (哈希预留长字段)
    trade_password_hash: Mapped[str] = mapped_column(String(256), nullable=True)
    # 取款密码 (哈希预留)
    withdraw_password_hash: Mapped[str] = mapped_column(String(256), nullable=True)
    # 可用资金 (默认 0, 使用 Decimal(18,2))
    available_funds: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"))
    # 冻结资金 (默认 0)
    frozen_funds: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"))
    # 总资金 (默认 0)
    total_funds: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"))
    # 账户状态
    account_status: Mapped[str] = mapped_column(
        String(16), default=AccountStatus.NORMAL.value, index=True
    )
    # 创建时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    # 更新时间
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class FundTransactionRecord(Base):
    """资金流水表"""
    __tablename__ = "fund_transaction_records"

    # 流水号 (主键)
    transaction_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    # 资金账户号
    fund_account_id: Mapped[str] = mapped_column(
        String(32), nullable=False, index=True
    )
    # 业务订单号
    business_order_id: Mapped[str] = mapped_column(String(64), nullable=True, index=True)
    # 变动类型: FREEZE / RELEASE / DEDUCT / INCREASE
    transaction_type: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    # 变动金额 (使用 Decimal(18,2))
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    # 变动原因
    reason: Mapped[str] = mapped_column(String(256), nullable=True)
    # 发生时间
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_fund_account_occurred", "fund_account_id", "occurred_at"),
    )
