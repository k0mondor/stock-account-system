"""认证API"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    LoginRequest,
    LoginResponse,
    PasswordChangeRequest,
    PasswordChangeResponse,
)
from app.services import auth_service
from app.utils.exceptions import AuthenticationException

router = APIRouter(prefix="/api/v1/account/auth", tags=["auth"])


@router.post("/login", response_model=dict)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None),
):
    """投资者登录"""
    try:
        result = auth_service.authenticate_user(db, request.fund_account_id, request.password)
        
        return {
            "success": True,
            "data": LoginResponse(
                verified=result["verified"],
                investor_id=result["investor_id"],
                fund_account_id=result["fund_account_id"],
                security_account_id=result["security_account_id"],
                token=result["token"],
                token_type=result["token_type"],
                expires_at=datetime.utcnow(),
            ),
            "code": 0,
            "message": "login success",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "code": 40101,
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.post("/password", response_model=dict)
async def change_password(
    request: PasswordChangeRequest,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None),
):
    """修改账户密码"""
    try:
        auth_service.change_password(
            db,
            request.fund_account_id,
            request.old_password,
            request.new_password,
            request.password_type,
        )
        
        return {
            "success": True,
            "data": PasswordChangeResponse(
                success=True,
                fund_account_id=request.fund_account_id,
                password_type=request.password_type,
                changed_at=datetime.utcnow(),
            ),
            "code": 0,
            "message": "password changed successfully",
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
