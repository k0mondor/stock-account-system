"""账户关联API"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    AssociationCheckRequest,
    AssociationCheckResponse,
    AssociationResponse,
)
from app.services import association_service

router = APIRouter(prefix="/api/v1/account/associations", tags=["association"])


@router.get("/", response_model=dict)
async def get_association(
    fund_account_id: Optional[str] = Query(None, description="资金账户号"),
    security_account_id: Optional[str] = Query(None, description="证券账户号"),
    investor_id: Optional[str] = Query(None, description="投资者编号"),
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None),
):
    """查询账户关联"""
    try:
        data = association_service.get_association_info(
            db,
            fund_account_id=fund_account_id,
            security_account_id=security_account_id,
            investor_id=investor_id,
        )
        return {
            "success": True,
            "data": AssociationResponse(**data),
            "code": 0,
            "message": "success",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "code": 40401,
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.get("/check", response_model=dict)
async def check_association(
    fund_account_id: str = Query(..., description="资金账户号"),
    security_account_id: str = Query(..., description="证券账户号"),
    operation_type: str = Query(..., description="业务类型"),
    investor_id: Optional[str] = Query(None, description="投资者编号"),
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None),
):
    """账户关联业务校验"""
    try:
        data = association_service.check_association(
            db,
            fund_account_id=fund_account_id,
            security_account_id=security_account_id,
            operation_type=operation_type,
            investor_id=investor_id,
        )
        return {
            "success": True,
            "data": AssociationCheckResponse(**data),
            "code": 0,
            "message": "success",
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
