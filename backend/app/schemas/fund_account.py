from datetime import datetime
from decimal import Decimal

from pydantic import Field

from app.core.enums import AccountStatus
from app.schemas.common import OrmModel


class FundAccountCreateRequest(OrmModel):
    """创建资金账户 - 请求参数"""
    fund_account_id: str = Field(
        ..., min_length=8, max_length=32,
        examples=["FUND000001"],
        description="资金账户号"
    )
    investor_id: str = Field(
        ..., min_length=8, max_length=32,
        examples=["INVESTOR001"],
        description="投资者编号"
    )
    bank_card_no: str = Field(
        ..., min_length=8, max_length=32,
        examples=["6222021234567890123"],
        description="绑定的银行卡号"
    )


class FundAccountResponse(OrmModel):
    """资金账户 - 响应结构"""
    fund_account_id: str
    investor_id: str
    bank_card_no: str
    available_balance: Decimal = Decimal("0.00")
    frozen_amount: Decimal = Decimal("0.00")
    total_amount: Decimal = Decimal("0.00")
    account_status: AccountStatus
    created_at: datetime
    updated_at: datetime
