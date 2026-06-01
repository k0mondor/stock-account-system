"""账户关联相关的Pydantic Schema"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AssociationQueryRequest(BaseModel):
    """账户关联查询请求"""
    fund_account_id: Optional[str] = Field(None, description="资金账户号")
    security_account_id: Optional[str] = Field(None, description="证券账户号")
    investor_id: Optional[str] = Field(None, description="投资者编号")


class AssociationResponse(BaseModel):
    """账户关联响应"""
    association_id: Optional[str] = Field(None, description="关联ID")
    investor_id: str = Field(..., description="投资者编号")
    fund_account_id: str = Field(..., description="资金账户号")
    security_account_id: str = Field(..., description="证券账户号")
    association_status: str = Field(..., description="关联状态：ACTIVE/UNLINKED")
    associated_at: Optional[datetime] = Field(None, description="关联时间")
    
    class Config:
        from_attributes = True


class AssociationCheckRequest(BaseModel):
    """账户关联业务校验请求"""
    fund_account_id: str = Field(..., description="资金账户号")
    security_account_id: str = Field(..., description="证券账户号")
    operation_type: str = Field(..., description="业务类型：BUY_ORDER/SELL_ORDER/CANCEL_ORDER/SETTLEMENT/ACCOUNT_FREEZE")
    investor_id: Optional[str] = Field(None, description="投资者编号")


class AssociationCheckResponse(BaseModel):
    """账户关联业务校验响应"""
    is_valid: bool = Field(..., description="是否有效绑定")
    association_status: str = Field(..., description="关联状态")
    fund_account_status: str = Field(..., description="资金账户状态")
    security_account_status: str = Field(..., description="证券账户状态")
    is_operation_allowed: bool = Field(..., description="当前业务是否允许")
    error_message: Optional[str] = Field(None, description="错误信息")
