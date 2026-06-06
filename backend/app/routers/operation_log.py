from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.auth_dependencies import require_service_token
from app.core.time import to_utc_naive
from app.schemas.common import ApiResponse
from app.schemas.operation_log import OperationLogCreate, OperationLogResponse
from app.services import operation_log_service

router = APIRouter(dependencies=[Depends(require_service_token)])


@router.post(
    "",
    response_model=ApiResponse[OperationLogResponse],
    status_code=status.HTTP_201_CREATED,
    summary="创建操作日志",
    description="记录一条操作日志（供内部模块调用）。",
)
def create_operation_log(
    payload: OperationLogCreate,
    db: Session = Depends(get_db),
) -> ApiResponse[OperationLogResponse]:
    try:
        log_entry = operation_log_service.create_operation_log(db, payload)
        db.commit()
        db.refresh(log_entry)
    except Exception:
        db.rollback()
        raise
    return ApiResponse.ok(
        data=OperationLogResponse.model_validate(log_entry),
        message="日志记录成功",
    )


@router.get(
    "",
    response_model=ApiResponse[dict],
    summary="查询操作日志",
    description="查询操作日志列表，支持多条件筛选和分页。",
)
def list_operation_logs(
    operator_id: str | None = Query(None, description="操作人员 ID"),
    operation_type: str | None = Query(None, description="操作类型"),
    target_type: str | None = Query(None, description="目标类型"),
    target_id: str | None = Query(None, description="目标 ID"),
    operation_result: str | None = Query(None, description="操作结果"),
    start_time: datetime | None = Query(None, description="开始时间 (ISO 8601)"),
    end_time: datetime | None = Query(None, description="结束时间 (ISO 8601)"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
) -> ApiResponse[dict]:
    if start_time:
        start_time = to_utc_naive(start_time)
    if end_time:
        end_time = to_utc_naive(end_time)
    if start_time and end_time and start_time > end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="开始时间不能晚于结束时间",
        )
    logs, total = operation_log_service.list_operation_logs(
        db,
        operator_id=operator_id,
        operation_type=operation_type,
        target_type=target_type,
        target_id=target_id,
        operation_result=operation_result,
        start_time=start_time,
        end_time=end_time,
        page=page,
        page_size=page_size,
    )

    items = [OperationLogResponse.model_validate(log_entry) for log_entry in logs]

    return ApiResponse.ok(
        data={
            "items": items,
            "page": page,
            "page_size": page_size,
            "total": total,
        },
        message="查询成功",
    )
