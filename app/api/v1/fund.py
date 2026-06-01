"""资金账户API"""

from decimal import Decimal
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Header, Path
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    FundAccountResponse,
    FundFreezeRequest,
    FundFreezeResponse,
    FundReleaseRequest,
    FundReleaseResponse,
    FundSettlementRequest,
    FundSettlementResponse,
)
from app.services import fund_service
import uuid

router = APIRouter(prefix="/api/v1/account", tags=["fund"])


@router.get("/fund-accounts/{fund_account_id}", response_model=dict)
async def get_fund_account(
    fund_account_id: str = Path(..., description="资金账户号"),
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None),
):
    """查询资金账户"""
    try:
        data = fund_service.get_fund_account_info(db, fund_account_id)
        return {
            "success": True,
            "data": FundAccountResponse(**data),
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


@router.post("/fund-accounts/{fund_account_id}/freeze", response_model=dict)
async def freeze_fund(
    fund_account_id: str = Path(..., description="资金账户号"),
    request: FundFreezeRequest = None,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None),
):
    """冻结资金"""
    try:
        freeze_id = f"FRZ{uuid.uuid4().hex[:20].upper()}"
        data = fund_service.freeze_fund(
            db,
            fund_account_id,
            freeze_id,
            request.order_id,
            Decimal(request.freeze_amount),
            request.freeze_reason,
        )
        return {
            "success": True,
            "data": FundFreezeResponse(**data),
            "code": 0,
            "message": "fund frozen successfully",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "code": 50201,
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.post("/fund-accounts/{fund_account_id}/release", response_model=dict)
async def release_fund(
    fund_account_id: str = Path(..., description="资金账户号"),
    request: FundReleaseRequest = None,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None),
):
    """释放资金"""
    try:
        data = fund_service.release_fund(
            db,
            fund_account_id,
            request.order_id,
            request.reason,
        )
        return {
            "success": True,
            "data": FundReleaseResponse(**data),
            "code": 0,
            "message": "fund released successfully",
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


@router.post("/fund-accounts/{fund_account_id}/settlements", response_model=dict)
async def settlement_fund(
    fund_account_id: str = Path(..., description="资金账户号"),
    request: FundSettlementRequest = None,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None),
):
    """资金结算"""
    try:
        settlement_id = f"STL{uuid.uuid4().hex[:20].upper()}"
        data = fund_service.settlement_fund(
            db,
            fund_account_id,
            settlement_id,
            request.message_id,
            request.settlement_type,
            Decimal(request.settlement_amount),
            request.reason,
            request.order_id,
            request.trade_id,
        )
        return {
            "success": True,
            "data": FundSettlementResponse(**data),
            "code": 0,
            "message": "fund settled successfully",
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
