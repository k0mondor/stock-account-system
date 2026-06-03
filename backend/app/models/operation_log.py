from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class OperationLog(Base):
    """操作日志表 — 记录所有账户相关操作的审计日志"""
    __tablename__ = "operation_logs"

    log_id: Mapped[str] = mapped_column(String(32), primary_key=True, index=True)
    operator_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    operator_name: Mapped[str] = mapped_column(String(64), nullable=False)
    operation_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(32), nullable=False)
    target_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    operation_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    operation_result: Mapped[str] = mapped_column(String(16), nullable=False, default="SUCCESS")
    fail_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    client_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
