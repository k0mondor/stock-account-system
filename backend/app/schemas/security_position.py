from decimal import Decimal

from pydantic import BaseModel, Field

from app.core.enums import PositionChangeType
from app.schemas.common import OrmModel


class SecurityPositionResponse(OrmModel):
    security_account_id: str
    investor_id: str
    stock_code: str
    stock_name: str | None
    total_quantity: int
    available_quantity: int
    frozen_quantity: int
    cost_price: Decimal | None


class SecurityPositionListResponse(BaseModel):
    security_account_id: str
    positions: list[SecurityPositionResponse]


class PositionChangeRequest(BaseModel):
    order_id: str = Field(..., min_length=1, max_length=64)
    stock_code: str = Field(..., pattern=r"^\d{6}$")
    quantity: int = Field(..., gt=0)
    reason: str | None = Field(None, max_length=256)


class PositionSettlementRequest(PositionChangeRequest):
    message_id: str = Field(..., min_length=1, max_length=64)
    trade_id: str = Field(..., min_length=1, max_length=64)
    change_type: PositionChangeType
    stock_name: str | None = Field(None, max_length=64)
    cost_price: Decimal | None = Field(None, gt=0, max_digits=18, decimal_places=4)


class PositionChangeResponse(BaseModel):
    record_id: str
    security_account_id: str
    business_order_id: str
    stock_code: str
    change_type: PositionChangeType
    changed_quantity: int
    total_quantity: int
    available_quantity: int
    frozen_quantity: int
