from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth_dependencies import require_service_token
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.joint_account import (
    JointAccountCloseRequest,
    JointAccountCloseResponse,
)
from app.services import joint_account_service

router = APIRouter()


@router.post(
    "/close",
    response_model=ApiResponse[JointAccountCloseResponse],
    status_code=status.HTTP_200_OK,
    summary="联合销户",
    description="在一个事务中同时关闭资金账户、证券账户并结束当前唯一有效绑定。",
)
def close_joint_accounts(
    payload: JointAccountCloseRequest,
    claims: dict = Depends(require_service_token),
    db: Session = Depends(get_db),
) -> ApiResponse[JointAccountCloseResponse]:
    del claims
    try:
        result = joint_account_service.close_joint_accounts(
            db,
            fund_account_id=payload.fund_account_id,
            security_account_id=payload.security_account_id,
            customer_id_number=payload.customer_id_number,
            operator_id=payload.operator_id,
            operator_name=payload.operator_name,
            reason=payload.reason,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return ApiResponse.ok(
        JointAccountCloseResponse(**result),
        "联合销户成功",
    )
