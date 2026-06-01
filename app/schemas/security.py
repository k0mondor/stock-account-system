"""证券账户相关的Pydantic Schema"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class SecurityPositionItem(BaseModel):
    """证券持仓项"""
    stock_code: str = Field(..., description="股票代码")
    stock_name: Optional[str] = Field(None, description="股票名称")
    total_quantity: int = Field(..., description="总持仓")
    available_quantity: int = Field(..., description="可卖数量")
    frozen_quantity: int = Field(..., description="冻结数量")
    cost_price: Optional[str] = Field(None, description="持仓成本")
    
    class Config:
        from_attributes = True


class SecurityPositionListResponse(BaseModel):
    """证券持仓列表响应"""
    security_account_id: str = Field(..., description="证券账户号")
    positions: List[SecurityPositionItem] = Field(..., description="持仓列表")


class PositionFreezeRequest(BaseModel):
    """冻结持仓请求"""
    order_id: str = Field(..., description="指令编号")
    freeze_quantity: int = Field(..., description="冻结数量")
    stock_code: str = Field(..., description="股票代码")
    reason: str = Field(..., description="冻结原因")


class PositionFreezeResponse(BaseModel):
    """冻结持仓响应"""
    freeze_id: str = Field(..., description="冻结记录ID")
    security_account_id: str = Field(..., description="证券账户号")
    stock_code: str = Field(..., description="股票代码")
    freeze_quantity: int = Field(..., description="冻结数量")
    available_quantity: int = Field(..., description="冻结后可卖数量")
    created_at: datetime = Field(..., description="冻结时间")


class PositionReleaseRequest(BaseModel):
    """释放持仓请求"""
    order_id: str = Field(..., description="指令编号")
    release_quantity: int = Field(..., description="释放数量")
    stock_code: str = Field(..., description="股票代码")
    reason: str = Field(..., description="释放原因")


class PositionReleaseResponse(BaseModel):
    """释放持仓响应"""
    security_account_id: str = Field(..., description="证券账户号")
    stock_code: str = Field(..., description="股票代码")
    release_quantity: int = Field(..., description="释放数量")
    available_quantity: int = Field(..., description="释放后可卖数量")


class PositionSettlementRequest(BaseModel):
    """证券结算请求"""
    message_id: str = Field(..., description="消息ID")
    order_id: Optional[str] = Field(None, description="指令编号")
    trade_id: Optional[str] = Field(None, description="成交编号")
    stock_code: str = Field(..., description="股票代码")
    settlement_type: str = Field(..., description="结算类型：DEDUCT/INCREASE")
    settlement_quantity: int = Field(..., description="结算数量")
    reason: str = Field(..., description="结算原因")


class PositionSettlementResponse(BaseModel):
    """证券结算响应"""
    settlement_id: str = Field(..., description="结算记录ID")
    security_account_id: str = Field(..., description="证券账户号")
    stock_code: str = Field(..., description="股票代码")
    settlement_quantity: int = Field(..., description="结算数量")
    settlement_type: str = Field(..., description="结算类型")
    total_quantity_after: int = Field(..., description="结算后总持仓")
    available_quantity_after: int = Field(..., description="结算后可卖数量")
    frozen_quantity_after: int = Field(..., description="结算后冻结数量")
