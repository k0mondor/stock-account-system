"""账户申请API"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    AccountApplicationSubmitRequest,
    AccountApplicationResponse,
    ApplicationQueryRequest,
    ApprovalRequest,
    ApprovalResponse,
    ApprovalHistoryResponse,
)
from app.services import application_service

router = APIRouter(prefix="/api/v1/account/applications", tags=["application"])


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
        return {
            "success": True,
            "data": AccountApplicationResponse(**data),
            "code": 0,
            "message": "申请提交成功",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "code": 40001,
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


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
        return {
            "success": True,
            "data": [AccountApplicationResponse(**item) for item in data],
            "code": 0,
            "message": "查询成功",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "code": 40001,
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


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
            return {
                "success": False,
                "data": None,
                "code": 40401,
                "message": "申请不存在",
                "timestamp": datetime.utcnow().isoformat(),
            }
        return {
            "success": True,
            "data": AccountApplicationResponse(**data[0]),
            "code": 0,
            "message": "查询成功",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "code": 40001,
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.post("/approve", response_model=dict)
async def approve_application(
    request: ApprovalRequest,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None),
):
    """审批通过申请"""
    try:
        if request.action != "APPROVE":
            return {
                "success": False,
                "data": None,
                "code": 40001,
                "message": "操作类型错误",
                "timestamp": datetime.utcnow().isoformat(),
            }
        
        data = application_service.approve_application(
            db,
            request.application_id,
            request.approver_id,
            request.approver_name,
            request.reason,
        )
        return {
            "success": True,
            "data": ApprovalResponse(**data),
            "code": 0,
            "message": "审批通过成功，账户已创建",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "code": 50001,
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.post("/reject", response_model=dict)
async def reject_application(
    request: ApprovalRequest,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None),
):
    """拒绝申请"""
    try:
        if request.action != "REJECT":
            return {
                "success": False,
                "data": None,
                "code": 40001,
                "message": "操作类型错误",
                "timestamp": datetime.utcnow().isoformat(),
            }
        
        data = application_service.reject_application(
            db,
            request.application_id,
            request.approver_id,
            request.approver_name,
            request.reason,
        )
        return {
            "success": True,
            "data": ApprovalResponse(**data),
            "code": 0,
            "message": "申请已拒绝",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "code": 50001,
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.get("/{application_id}/approval-history", response_model=dict)
async def get_approval_history(
    application_id: str,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None),
):
    """获取审批历史"""
    try:
        data = application_service.get_approval_history(db, application_id)
        return {
            "success": True,
            "data": ApprovalHistoryResponse(**data),
            "code": 0,
            "message": "查询成功",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "code": 40001,
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
