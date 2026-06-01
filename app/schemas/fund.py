"""资金账户相关的Pydantic Schema"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class FundAccountResponse(BaseModel):
    """资金账户响应"""
    fund_account_id: str = Field(..., description="资金账户号")
    investor_id: str = Field(..., description="投资者编号")
    available_amount: str = Field(..., description="可用资金")
    frozen_amount: str = Field(..., description="冻结资金")
    total_amount: str = Field(..., description="总资金")
    status: str = Field(..., description="账户状态")
    
    class Config:
        from_attributes = True


class FundFreezeRequest(BaseModel):
    """冻结资金请求"""
    order_id: str = Field(..., description="指令编号")
    freeze_amount: str = Field(..., description="冻结金额")
    freeze_reason: str = Field(..., description="冻结原因")
    requested_at: datetime = Field(..., description="请求时间")


class FundFreezeResponse(BaseModel):
    """冻结资金响应"""
    freeze_id: str = Field(..., description="冻结记录ID")
    fund_account_id: str = Field(..., description="资金账户号")
    freeze_amount: str = Field(..., description="冻结金额")
    available_amount: str = Field(..., description="冻结后可用资金")
    created_at: datetime = Field(..., description="冻结时间")


class FundReleaseRequest(BaseModel):
    """释放资金请求"""
    order_id: str = Field(..., description="指令编号")
    release_amount: str = Field(..., description="释放金额")
    reason: str = Field(..., description="释放原因")


class FundReleaseResponse(BaseModel):
    """释放资金响应"""
    fund_account_id: str = Field(..., description="资金账户号")
    release_amount: str = Field(..., description="释放金额")
    available_amount: str = Field(..., description="释放后可用资金")


class FundSettlementRequest(BaseModel):
    """资金结算请求"""
    message_id: str = Field(..., description="消息ID")
    order_id: Optional[str] = Field(None, description="指令编号")
    trade_id: Optional[str] = Field(None, description="成交编号")
    settlement_type: str = Field(..., description="结算类型：DEDUCT/INCREASE")
    settlement_amount: str = Field(..., description="结算金额")
    reason: str = Field(..., description="结算原因")


class FundSettlementResponse(BaseModel):
    """资金结算响应"""
    settlement_id: str = Field(..., description="结算记录ID")
    fund_account_id: str = Field(..., description="资金账户号")
    settlement_amount: str = Field(..., description="结算金额")
    settlement_type: str = Field(..., description="结算类型")
    available_amount_after: str = Field(..., description="结算后可用资金")
    frozen_amount_after: str = Field(..., description="结算后冻结资金")
    total_amount_after: str = Field(..., description="结算后总资金")
