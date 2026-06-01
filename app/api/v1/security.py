"""证券账户API"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Header, Path, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    SecurityPositionListResponse,
    PositionFreezeRequest,
    PositionFreezeResponse,
    PositionReleaseRequest,
    PositionReleaseResponse,
    PositionSettlementRequest,
    PositionSettlementResponse,
)
from app.services import security_service
import uuid

router = APIRouter(prefix="/api/v1/account", tags=["security"])


@router.get("/security-accounts/{security_account_id}/positions", response_model=dict)
async def get_positions(
    security_account_id: str = Path(..., description="证券账户号"),
    stock_code: Optional[str] = Query(None, description="股票代码"),
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None),
):
    """查询证券持仓"""
    try:
        data = security_service.get_positions_info(db, security_account_id, stock_code)
        return {
            "success": True,
            "data": SecurityPositionListResponse(**data),
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


@router.post("/security-accounts/{security_account_id}/positions/freeze", response_model=dict)
async def freeze_position(
    security_account_id: str = Path(..., description="证券账户号"),
    request: PositionFreezeRequest = None,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None),
):
    """冻结证券持仓"""
    try:
        freeze_id = f"PFZ{uuid.uuid4().hex[:20].upper()}"
        position_id = f"POS{uuid.uuid4().hex[:20].upper()}"
        
        data = security_service.freeze_position(
            db,
            security_account_id,
            freeze_id,
            position_id,
            request.order_id,
            request.stock_code,
            request.freeze_quantity,
            request.reason,
        )
        return {
            "success": True,
            "data": PositionFreezeResponse(**data),
            "code": 0,
            "message": "position frozen successfully",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "code": 50202,
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.post("/security-accounts/{security_account_id}/positions/release", response_model=dict)
async def release_position(
    security_account_id: str = Path(..., description="证券账户号"),
    request: PositionReleaseRequest = None,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None),
):
    """释放证券持仓"""
    try:
        data = security_service.release_position(
            db,
            security_account_id,
            request.order_id,
            request.reason,
        )
        return {
            "success": True,
            "data": PositionReleaseResponse(**data),
            "code": 0,
            "message": "position released successfully",
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


@router.post("/security-accounts/{security_account_id}/positions/settlements", response_model=dict)
async def settlement_position(
    security_account_id: str = Path(..., description="证券账户号"),
    request: PositionSettlementRequest = None,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None),
):
    """证券结算"""
    try:
        settlement_id = f"PST{uuid.uuid4().hex[:20].upper()}"
        position_id = f"POS{uuid.uuid4().hex[:20].upper()}"
        
        data = security_service.settlement_position(
            db,
            security_account_id,
            settlement_id,
            position_id,
            request.message_id,
            request.stock_code,
            request.settlement_type,
            request.settlement_quantity,
            request.reason,
            request.order_id,
            request.trade_id,
        )
        return {
            "success": True,
            "data": PositionSettlementResponse(**data),
            "code": 0,
            "message": "position settled successfully",
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
