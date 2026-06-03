from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import AssociationStatus
from app.db.session import Base


class AccountAssociation(Base):
    """账户关联表 — 资金账户与证券账户的一对一绑定关系"""
    __tablename__ = "account_associations"

    association_id: Mapped[str] = mapped_column(String(32), primary_key=True, index=True)
    investor_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    fund_account_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    security_account_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    association_status: Mapped[str] = mapped_column(
        String(16), default=AssociationStatus.ACTIVE.value, index=True
    )
    associated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
