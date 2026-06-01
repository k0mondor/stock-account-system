from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import CustomerStatus, StaffRole, StaffStatus
from app.db.session import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[str] = mapped_column(String(32), primary_key=True, index=True)
    customer_name: Mapped[str] = mapped_column(String(64), nullable=False)
    id_number: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    customer_status: Mapped[str] = mapped_column(String(16), default=CustomerStatus.ACTIVE.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Staff(Base):
    __tablename__ = "staff"

    staff_id: Mapped[str] = mapped_column(String(32), primary_key=True, index=True)
    staff_name: Mapped[str] = mapped_column(String(64), nullable=False)
    role: Mapped[str] = mapped_column(String(16), default=StaffRole.STAFF.value, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    staff_status: Mapped[str] = mapped_column(String(16), default=StaffStatus.ACTIVE.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
