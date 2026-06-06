from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.time import utc_now
from app.db.session import Base


class SecurityPosition(Base):
    __tablename__ = "security_positions"

    position_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    security_account_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("securities_accounts.security_account_id"),
        nullable=False,
        index=True,
    )
    investor_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("customers.customer_id"), nullable=False, index=True
    )
    stock_code: Mapped[str] = mapped_column(String(6), nullable=False, index=True)
    stock_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    total_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    available_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    frozen_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cost_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now
    )

    __table_args__ = (
        UniqueConstraint(
            "security_account_id",
            "stock_code",
            name="uq_security_position_stock",
        ),
    )


class PositionTransactionRecord(Base):
    __tablename__ = "position_transaction_records"

    record_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    security_account_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("securities_accounts.security_account_id"),
        nullable=False,
        index=True,
    )
    business_order_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    trade_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    stock_code: Mapped[str] = mapped_column(String(6), nullable=False, index=True)
    change_type: Mapped[str] = mapped_column(String(16), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str | None] = mapped_column(String(256), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, index=True)

    __table_args__ = (
        Index(
            "idx_position_account_time",
            "security_account_id",
            "occurred_at",
        ),
        UniqueConstraint(
            "security_account_id",
            "business_order_id",
            "change_type",
            "stock_code",
            name="uq_position_transaction_business",
        ),
    )
