from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.fund_account import FundAccount
from app.schemas.common import ApiResponse
from app.schemas.fund_account import FundAccountCreateRequest, FundAccountResponse

router = APIRouter()


@router.post(
    "",
    response_model=ApiResponse[FundAccountResponse],
    status_code=status.HTTP_201_CREATED,
    summary="创建资金账户",
    description="为投资者开设一个新的资金账户，初始化余额为 0。",
)
def create_fund_account(
    request: FundAccountCreateRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[FundAccountResponse]:
    """
    创建资金账户接口：

    - **fund_account_id**: 资金账户号（唯一主键）
    - **investor_id**: 投资者编号
    - **bank_card_no**: 绑定的银行卡号

    账户创建时：
    - 可用资金、冻结资金、总资金均初始化为 0
    - 账户状态默认为 NORMAL
    """
    # 校验账号是否已存在
    existing = db.query(FundAccount).filter(
        FundAccount.fund_account_id == request.fund_account_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"资金账户号 {request.fund_account_id} 已存在",
        )

    # 创建新账户
    fund_account = FundAccount(
        fund_account_id=request.fund_account_id,
        investor_id=request.investor_id,
        bank_card_no=request.bank_card_no,
    )
    db.add(fund_account)
    db.commit()
    db.refresh(fund_account)

    return ApiResponse.ok(
        data=FundAccountResponse.model_validate(fund_account),
        message="资金账户创建成功",
    )


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
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"资金账户 {fund_account_id} 不存在",
        )

    return ApiResponse.ok(
        data=FundAccountResponse.model_validate(fund_account),
        message="查询成功",
    )
