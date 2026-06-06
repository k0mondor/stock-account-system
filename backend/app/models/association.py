from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import AssociationStatus
from app.core.time import utc_now
from app.db.session import Base


class AccountAssociation(Base):
    """账户关联表 — 资金账户与证券账户的一对一绑定关系"""
    __tablename__ = "account_associations"

    association_id: Mapped[str] = mapped_column(String(32), primary_key=True, index=True)
    investor_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("customers.customer_id"), nullable=False, index=True
    )
    fund_account_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("fund_accounts.fund_account_id"), nullable=False, index=True
    )
    security_account_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("securities_accounts.security_account_id"),
        nullable=False,
        index=True,
    )
    association_status: Mapped[str] = mapped_column(
        String(16), default=AssociationStatus.ACTIVE.value, index=True
    )
    associated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    disassociated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now
    )

    __table_args__ = (
        Index(
            "uq_active_association_fund",
            "fund_account_id",
            unique=True,
            sqlite_where=text("association_status = 'ACTIVE'"),
        ).ddl_if(dialect="sqlite"),
        Index(
            "uq_active_association_security",
            "security_account_id",
            unique=True,
            sqlite_where=text("association_status = 'ACTIVE'"),
        ).ddl_if(dialect="sqlite"),
    )
