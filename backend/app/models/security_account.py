from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import AccountStatus
from app.core.time import utc_now
from app.db.session import Base


class SecuritiesAccount(Base):
    """证券账户表。证券账户仅由联合开户流程创建。"""

    __tablename__ = "securities_accounts"

    security_account_id: Mapped[str] = mapped_column(
        String(32), primary_key=True, index=True
    )
    investor_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("customers.customer_id"), nullable=False, index=True
    )
    security_password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    account_status: Mapped[str] = mapped_column(
        String(16), default=AccountStatus.NORMAL.value, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now
    )
