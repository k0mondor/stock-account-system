from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_serializer

from app.core.enums import AccountStatus, FundChangeType, PasswordType
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

    @field_serializer("bank_card_no")
    def serialize_bank_card_no(self, value: str) -> str:
        if len(value) <= 8:
            return "*" * len(value)
        return f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}"


class FundOperationRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, max_digits=18, decimal_places=2)
    business_order_id: str | None = Field(None, max_length=64)
    reason: str | None = Field(None, max_length=256)
    operator_id: str = Field("SYSTEM", min_length=1, max_length=32)
    operator_name: str = Field("系统", min_length=1, max_length=64)


class FundWithdrawRequest(FundOperationRequest):
    withdraw_password: str = Field(..., min_length=6, max_length=64)


class FundTransactionResponse(OrmModel):
    transaction_id: str
    fund_account_id: str
    business_order_id: str | None
    operator_staff_id: str | None
    transaction_type: str
    amount: Decimal
    reason: str | None
    occurred_at: datetime
    available_amount: Decimal
    frozen_amount: Decimal
    total_amount: Decimal


class AccountCloseRequest(BaseModel):
    customer_id_number: str = Field(..., min_length=1, max_length=32)
    operator_id: str = Field("SYSTEM", min_length=1, max_length=32)
    operator_name: str = Field("系统", min_length=1, max_length=64)


class FundTradeChangeRequest(BaseModel):
    order_id: str = Field(..., min_length=1, max_length=64)
    amount: Decimal = Field(..., gt=0, max_digits=18, decimal_places=2)
    reason: str | None = Field(None, max_length=256)
    requested_at: datetime | None = None


class FundSettlementRequest(BaseModel):
    message_id: str = Field(..., min_length=1, max_length=64)
    trade_id: str = Field(..., min_length=1, max_length=64)
    order_id: str = Field(..., min_length=1, max_length=64)
    change_type: FundChangeType
    amount: Decimal = Field(..., gt=0, max_digits=18, decimal_places=2)
    reason: str | None = Field(None, max_length=256)


class FundTradeChangeResponse(BaseModel):
    transaction_id: str
    fund_account_id: str
    business_order_id: str
    change_type: FundChangeType
    changed_amount: Decimal
    available_amount: Decimal
    frozen_amount: Decimal
    total_amount: Decimal


class AccountStateChangeRequest(BaseModel):
    customer_id_number: str = Field(..., min_length=1, max_length=32)
    reason: str | None = Field(None, max_length=256)
    operator_id: str = Field("SYSTEM", min_length=1, max_length=32)
    operator_name: str = Field("系统", min_length=1, max_length=64)


class StaffPasswordResetRequest(BaseModel):
    staff_id: str = Field(..., min_length=1, max_length=32)
    customer_id_number: str = Field(..., min_length=1, max_length=32)
    password_type: PasswordType
    new_password: str = Field(..., min_length=6, max_length=64)
    reason: str = Field(..., min_length=1, max_length=256)
