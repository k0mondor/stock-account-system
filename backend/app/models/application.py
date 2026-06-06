from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ApplicationStatus, ApprovalResult, ProcessStatus
from app.core.time import utc_now
from app.db.session import Base


class AccountApplication(Base):
    __tablename__ = "account_applications"

    application_id: Mapped[str] = mapped_column(String(32), primary_key=True, index=True)
    customer_id: Mapped[str] = mapped_column(String(32), ForeignKey("customers.customer_id"), index=True)
    applicant_name: Mapped[str] = mapped_column(String(64), nullable=False)
    id_number: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    app_status: Mapped[str] = mapped_column(String(16), default=ApplicationStatus.SUBMITTED.value, index=True)
    proc_status: Mapped[str] = mapped_column(String(16), default=ProcessStatus.PENDING.value, index=True)
    fund_account_id: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    security_account_id: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)


class ApprovalRecord(Base):
    __tablename__ = "approval_records"

    approval_id: Mapped[str] = mapped_column(String(32), primary_key=True, index=True)
    application_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("account_applications.application_id"),
        index=True,
    )
    approver_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("staff.staff_id"), nullable=False, index=True
    )
    approval_result: Mapped[str] = mapped_column(String(16), default=ApprovalResult.APPROVED.value)
    approval_opinion: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
