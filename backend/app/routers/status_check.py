from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.fund_account import FundAccount
from app.schemas.common import ApiResponse
from app.schemas.status_check import StatusCheckRequest, StatusCheckResponse
from app.core.enums import AccountStatus

router = APIRouter()

OPERATION_ALLOWED_STATUSES = {
    "BUY_ORDER": {AccountStatus.NORMAL.value},
    "SELL_ORDER": {AccountStatus.NORMAL.value},
    "CANCEL_ORDER": {AccountStatus.NORMAL.value, AccountStatus.FROZEN.value},
    "SETTLEMENT": {AccountStatus.NORMAL.value, AccountStatus.FROZEN.value},
    "ACCOUNT_FREEZE": {AccountStatus.NORMAL.value},
    "DEPOSIT": {AccountStatus.NORMAL.value},
    "WITHDRAW": {AccountStatus.NORMAL.value},
    "CHANGE_PWD": {AccountStatus.NORMAL.value},
    "LOST": {AccountStatus.NORMAL.value},
    "REISSUE": {AccountStatus.LOST.value},
    "CANCEL": {AccountStatus.NORMAL.value, AccountStatus.LOST.value},
    "QUERY": {
        AccountStatus.NORMAL.value,
        AccountStatus.FROZEN.value,
        AccountStatus.LOST.value,
    },
}


@router.post(
    "/check",
    response_model=ApiResponse[StatusCheckResponse],
    summary="账户状态校验",
    description="校验指定账户的当前状态是否允许执行特定操作。",
)
def check_status(
    payload: StatusCheckRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[StatusCheckResponse]:
    raw_type = payload.account_type.upper()
    # 兼容前端历史用法 SECURITIES，统一规范为 SECURITY
    account_type = "SECURITY" if raw_type in ("SECURITIES", "SECURITY") else raw_type
    account_id = payload.account_id
    operation_type = payload.operation_type.upper()

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
        return ApiResponse.ok(
            data=StatusCheckResponse(
                account_type=account_type,
                account_id=account_id,
                status="NORMAL",
                allowed=True,
                reason=None,
            ),
            message="校验完成",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的账户类型: {account_type}，仅支持 FUND 或 SECURITY",
        )

    allowed_statuses = OPERATION_ALLOWED_STATUSES.get(
        operation_type, {AccountStatus.NORMAL.value}
    )
    allowed = current_status in allowed_statuses

    reason = None
    if not allowed:
        status_reasons = {
            AccountStatus.FROZEN.value: "账户已冻结，不允许执行当前操作",
            AccountStatus.LOST.value: "账户已挂失，不允许执行当前操作",
            AccountStatus.CLOSED.value: "账户已注销，不允许执行当前操作",
        }
        reason = status_reasons.get(
            current_status, f"账户状态({current_status})不允许执行操作({operation_type})"
        )

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
