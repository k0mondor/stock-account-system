"""账户申请API"""

from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    AccountApplicationResponse,
    AccountApplicationSubmitRequest,
    ApprovalHistoryResponse,
    ApprovalRequest,
    ApprovalResponse,
)
from app.services import application_service
from app.utils.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
)

router = APIRouter(prefix="/api/v1/account/applications", tags=["application"])


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _success(data: Any, message: str, request_id: Optional[str] = None) -> dict:
    body = {
        "success": True,
        "data": data,
        "code": 0,
        "message": message,
        "timestamp": _timestamp(),
    }
    if request_id:
        body["request_id"] = request_id
    return body


def _failure(
    message: str,
    code: int,
    request_id: Optional[str] = None,
) -> dict:
    body = {
        "success": False,
        "data": None,
        "code": code,
        "message": message,
        "timestamp": _timestamp(),
    }
    if request_id:
        body["request_id"] = request_id
    return body


def _handle_service_error(exc: Exception, request_id: Optional[str] = None) -> dict:
    if isinstance(exc, NotFoundException):
        return _failure(str(exc.detail), 40401, request_id)
    if isinstance(exc, ConflictException):
        return _failure(str(exc.detail), 40900, request_id)
    if isinstance(exc, BadRequestException):
        return _failure(str(exc.detail), 40001, request_id)
    return _failure(str(exc), 50001, request_id)


@router.post("/submit", response_model=dict)
async def submit_application(
    request: AccountApplicationSubmitRequest,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None),
):
    """提交开户申请"""
    try:
        data = application_service.submit_application(
            db,
            request.username,
            request.real_name,
            request.id_card,
            request.phone,
            request.email,
        )
        return _success(
            AccountApplicationResponse(**data).model_dump(),
            "申请提交成功",
            x_request_id,
        )
    except Exception as e:
        return _handle_service_error(e, x_request_id)


@router.get("/query", response_model=dict)
async def query_applications(
    application_id: Optional[str] = Query(None, description="申请编号"),
    username: Optional[str] = Query(None, description="用户名"),
    id_card: Optional[str] = Query(None, description="身份证号"),
    status: Optional[str] = Query(None, description="申请状态"),
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None),
):
    """查询开户申请"""
    try:
        data = application_service.query_application(
            db,
            application_id=application_id,
            username=username,
            id_card=id_card,
            status=status,
        )
        items = [AccountApplicationResponse(**item).model_dump() for item in data]
        return _success(items, "查询成功", x_request_id)
    except Exception as e:
        return _handle_service_error(e, x_request_id)


@router.get("/{application_id}", response_model=dict)
async def get_application_detail(
    application_id: str,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None),
):
    """获取申请详情"""
    try:
        data = application_service.query_application(
            db,
            application_id=application_id,
        )
        if not data:
            return _failure("申请不存在", 40401, x_request_id)
        return _success(
            AccountApplicationResponse(**data[0]).model_dump(),
            "查询成功",
            x_request_id,
        )
    except Exception as e:
        return _handle_service_error(e, x_request_id)


@router.post("/approve", response_model=dict)
async def approve_application(
    request: ApprovalRequest,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None),
):
    """审批通过申请"""
    if request.action != "APPROVE":
        return _failure("操作类型错误", 40001, x_request_id)

    try:
        data = application_service.approve_application(
            db,
            request.application_id,
            request.approver_id,
            request.approver_name,
            request.reason,
        )
        return _success(
            ApprovalResponse(**data).model_dump(),
            "审批通过成功，账户已创建",
            x_request_id,
        )
    except Exception as e:
        return _handle_service_error(e, x_request_id)


@router.post("/reject", response_model=dict)
async def reject_application(
    request: ApprovalRequest,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None),
):
    """拒绝申请"""
    if request.action != "REJECT":
        return _failure("操作类型错误", 40001, x_request_id)

    try:
        data = application_service.reject_application(
            db,
            request.application_id,
            request.approver_id,
            request.approver_name,
            request.reason,
        )
        return _success(
            ApprovalResponse(**data).model_dump(),
            "申请已拒绝",
            x_request_id,
        )
    except Exception as e:
        return _handle_service_error(e, x_request_id)


@router.get("/{application_id}/approval-history", response_model=dict)
async def get_approval_history(
    application_id: str,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None),
):
    """获取审批历史"""
    try:
        data = application_service.get_approval_history(db, application_id)
        return _success(
            ApprovalHistoryResponse(**data).model_dump(),
            "查询成功",
            x_request_id,
        )
    except Exception as e:
        return _handle_service_error(e, x_request_id)
