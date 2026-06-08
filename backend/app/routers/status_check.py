from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.account_rules import allowed_statuses, status_rejection_reason
from app.core.auth_dependencies import require_access_token, require_service_token
from app.core.enums import AccountStatus
from app.db.session import get_db
from app.models.fund_account import FundAccount
from app.models.security_account import SecuritiesAccount
from app.schemas.common import ApiResponse
from app.schemas.status_check import (
    StatusChangeRequest,
    StatusCheckRequest,
    StatusCheckResponse,
    StatusHistoryResponse,
)
from app.services import account_state_service

router = APIRouter()


@router.get(
    "/history",
    response_model=ApiResponse[list[StatusHistoryResponse]],
    summary="查询账户状态变更历史",
)
def query_status_history(
    account_type: str,
    account_id: str,
    claims: dict = Depends(require_service_token),
    db: Session = Depends(get_db),
) -> ApiResponse[list[StatusHistoryResponse]]:
    del claims
    records = account_state_service.list_status_history(
        db,
        account_type=account_type,
        account_id=account_id,
    )
    return ApiResponse.ok(
        [StatusHistoryResponse.model_validate(item) for item in records],
        "查询成功",
    )


@router.post(
    "/check",
    response_model=ApiResponse[StatusCheckResponse],
    summary="账户状态校验",
    description="校验指定账户的当前状态是否允许执行特定操作。",
)
def check_status(
    payload: StatusCheckRequest,
    claims: dict = Depends(require_access_token),
    db: Session = Depends(get_db),
) -> ApiResponse[StatusCheckResponse]:
    raw_type = payload.account_type.upper()
    # 兼容前端历史用法 SECURITIES，统一规范为 SECURITY
    account_type = "SECURITY" if raw_type in ("SECURITIES", "SECURITY") else raw_type
    account_id = payload.account_id
    operation_type = payload.operation_type.upper()
    if account_type not in {"FUND", "SECURITY"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的账户类型: {account_type}，仅支持 FUND 或 SECURITY",
        )
    if claims["token_type"] != "SERVICE":
        expected_account_id = (
            claims["fund_account_id"]
            if account_type == "FUND"
            else claims["security_account_id"]
            if account_type == "SECURITY"
            else None
        )
        if expected_account_id != account_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="访问令牌与待校验账户不匹配",
            )

    if account_type == "FUND":
        account = db.get(FundAccount, account_id)
        if not account:
            return ApiResponse.ok(
                data=StatusCheckResponse(
                    account_type=account_type,
                    account_id=account_id,
                    status="NOT_FOUND",
                    allowed=False,
                    reason="账户不存在",
                ),
                message="校验完成",
            )
        current_status = account.account_status
    elif account_type == "SECURITY":
        account = db.get(SecuritiesAccount, account_id)
        if not account:
            return ApiResponse.ok(
                data=StatusCheckResponse(
                    account_type=account_type,
                    account_id=account_id,
                    status="NOT_FOUND",
                    allowed=False,
                    reason="账户不存在",
                ),
                message="校验完成",
            )
        current_status = account.account_status
    operation_statuses = allowed_statuses(operation_type)
    if operation_statuses is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的操作类型: {operation_type}",
        )
    allowed = current_status in operation_statuses

    reason = None
    if not allowed:
        reason = status_rejection_reason("账户", current_status)

    return ApiResponse.ok(
        data=StatusCheckResponse(
            account_type=account_type,
            account_id=account_id,
            status=current_status,
            allowed=allowed,
            reason=reason,
        ),
        message="校验完成",
    )


@router.post(
    "/change",
    response_model=ApiResponse[StatusCheckResponse],
    summary="冻结或解冻账户",
)
def change_status(
    payload: StatusChangeRequest,
    claims: dict = Depends(require_service_token),
    db: Session = Depends(get_db),
) -> ApiResponse[StatusCheckResponse]:
    del claims
    if payload.target_status not in {
        AccountStatus.FROZEN,
        AccountStatus.NORMAL,
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="通用状态变更接口仅支持冻结或解冻；挂失、补办和销户请使用对应业务接口",
        )
    raw_type = payload.account_type.upper()
    account_type = "SECURITY" if raw_type in {"SECURITY", "SECURITIES"} else raw_type
    model = (
        FundAccount
        if account_type == "FUND"
        else SecuritiesAccount
        if account_type == "SECURITY"
        else None
    )
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户类型仅支持 FUND 或 SECURITY",
        )
    account = db.get(model, payload.account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="账户不存在",
        )
    expected_status = (
        AccountStatus.NORMAL.value
        if payload.target_status == AccountStatus.FROZEN
        else AccountStatus.FROZEN.value
    )
    if account.account_status != expected_status:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "通用状态变更接口只允许正常账户冻结或冻结账户解冻；"
                "挂失账户恢复必须使用挂失补办接口"
            ),
        )
    if (
        payload.target_status == AccountStatus.NORMAL
        and account_state_service.is_linked_loss_freeze(
            db,
            account_type=account_type,
            account_id=payload.account_id,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该账户因关联账户挂失被自动冻结，必须通过对应挂失补办流程恢复",
        )
    try:
        account = account_state_service.change_status(
            db,
            account_type=payload.account_type,
            account_id=payload.account_id,
            target_status=payload.target_status,
            reason=payload.reason,
            operator_id=payload.operator_id,
            operator_name=payload.operator_name,
        )
        db.commit()
        db.refresh(account)
    except Exception:
        db.rollback()
        raise
    return ApiResponse.ok(
        StatusCheckResponse(
            account_type=account_type,
            account_id=payload.account_id,
            status=account.account_status,
            allowed=True,
            reason=None,
        ),
        "账户状态变更成功",
    )
