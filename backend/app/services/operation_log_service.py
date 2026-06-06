from datetime import datetime
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.request_context import get_request_id
from app.models.operation_log import OperationLog
from app.schemas.operation_log import OperationLogCreate


def _new_id(prefix: str) -> str:
    return f"{prefix}{uuid4().hex[:18].upper()}"


def create_operation_log(db: Session, payload: OperationLogCreate) -> OperationLog:
    """创建操作日志记录。"""
    log_entry = OperationLog(
        log_id=_new_id("LOG"),
        operator_id=payload.operator_id,
        operator_name=payload.operator_name,
        operation_type=payload.operation_type,
        target_type=payload.target_type,
        target_id=payload.target_id,
        operation_detail=payload.operation_detail,
        operation_result=payload.operation_result,
        fail_reason=payload.fail_reason,
        client_ip=payload.client_ip,
        request_id=payload.request_id,
    )
    db.add(log_entry)
    db.flush()
    return log_entry


def add_operation_log(
    db: Session,
    *,
    operator_id: str,
    operator_name: str,
    operation_type: str,
    target_type: str,
    target_id: str,
    operation_detail: str,
) -> OperationLog:
    """供业务服务在同一事务内写入审计日志。"""
    return create_operation_log(
        db,
        OperationLogCreate(
            operator_id=operator_id,
            operator_name=operator_name,
            operation_type=operation_type,
            target_type=target_type,
            target_id=target_id,
            operation_detail=operation_detail,
            request_id=get_request_id(),
        ),
    )


def list_operation_logs(
    db: Session,
    operator_id: str | None = None,
    operation_type: str | None = None,
    target_type: str | None = None,
    target_id: str | None = None,
    operation_result: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[OperationLog], int]:
    """查询操作日志列表，支持多条件筛选和分页。"""
    def _apply_filters(q):
        if operator_id:
            q = q.where(OperationLog.operator_id == operator_id)
        if operation_type:
            q = q.where(OperationLog.operation_type == operation_type)
        if target_type:
            q = q.where(OperationLog.target_type == target_type)
        if target_id:
            q = q.where(OperationLog.target_id == target_id)
        if operation_result:
            q = q.where(OperationLog.operation_result == operation_result)
        if start_time:
            q = q.where(OperationLog.created_at >= start_time)
        if end_time:
            q = q.where(OperationLog.created_at <= end_time)
        return q

    count_query = _apply_filters(select(func.count()).select_from(OperationLog))
    total = db.scalar(count_query) or 0

    offset = (page - 1) * page_size
    query = _apply_filters(select(OperationLog))
    query = query.order_by(OperationLog.created_at.desc()).offset(offset).limit(page_size)

    logs = list(db.scalars(query).all())
    return logs, total
