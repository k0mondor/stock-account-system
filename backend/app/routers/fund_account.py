from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.fund_account import FundAccount
from app.schemas.common import ApiResponse
from app.schemas.fund_account import FundAccountResponse

router = APIRouter()


@router.get(
    "/{fund_account_id}",
    response_model=ApiResponse[FundAccountResponse],
    summary="查询资金账户",
    description="根据资金账户号查询账户详细信息。",
)
def get_fund_account(
    fund_account_id: str,
    db: Session = Depends(get_db),
) -> ApiResponse[FundAccountResponse]:
    """
    查询资金账户接口：

    - **fund_account_id**: 资金账户号

    返回账户的完整信息，包括余额、状态等。
    """
    fund_account = db.query(FundAccount).filter(
        FundAccount.fund_account_id == fund_account_id
    ).first()
    if not fund_account:
        raise HTTPException(
            status_code=404,
            detail=f"资金账户 {fund_account_id} 不存在",
        )

    return ApiResponse.ok(
        data=FundAccountResponse.model_validate(fund_account),
        message="查询成功",
    )
