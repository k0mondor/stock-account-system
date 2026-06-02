from datetime import datetime
from decimal import Decimal

from pydantic import Field

from app.core.enums import AccountStatus
from app.schemas.common import OrmModel


class FundAccountResponse(OrmModel):
    """资金账户 - 响应结构"""
    fund_account_id: str
    investor_id: str
    bank_card_no: str
    available_amount: Decimal = Field(
        default=Decimal("0.00"),
        validation_alias="available_balance",
    )
    frozen_amount: Decimal = Field(
        default=Decimal("0.00"),
        validation_alias="frozen_amount",
    )
    total_amount: Decimal = Field(
        default=Decimal("0.00"),
        validation_alias="total_amount",
    )
    account_status: AccountStatus
    created_at: datetime
    updated_at: datetime
