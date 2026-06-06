from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.auth_dependencies import require_access_token
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    PasswordChangeRequest,
    PasswordChangeResponse,
)
from app.schemas.common import ApiResponse
from app.services import auth_service


router = APIRouter()


@router.post("/login", response_model=ApiResponse[LoginResponse], summary="交易客户端登录")
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[LoginResponse]:
    result = auth_service.login(db, payload.fund_account_id, payload.password)
    return ApiResponse.ok(LoginResponse(**result), "登录成功")


@router.post(
    "/password",
    response_model=ApiResponse[PasswordChangeResponse],
    summary="修改资金账户密码",
)
def change_password(
    payload: PasswordChangeRequest,
    claims: dict = Depends(require_access_token),
    db: Session = Depends(get_db),
) -> ApiResponse[PasswordChangeResponse]:
    if (
        claims["token_type"] != "SERVICE"
        and claims["fund_account_id"] != payload.fund_account_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="访问令牌与资金账户不匹配",
        )
    try:
        auth_service.change_password(
            db,
            fund_account_id=payload.fund_account_id,
            password_type=payload.password_type,
            old_password=payload.old_password,
            new_password=payload.new_password,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return ApiResponse.ok(
        PasswordChangeResponse(
            fund_account_id=payload.fund_account_id,
            password_type=payload.password_type,
            changed=True,
        ),
        "密码修改成功",
    )
