from datetime import datetime

from pydantic import BaseModel, Field


class StatusCheckRequest(BaseModel):
    """账户状态校验 - 请求"""
    account_type: str = Field(..., description="账户类型: FUND / SECURITIES")
    account_id: str = Field(..., description="账户 ID")
    operation_type: str = Field(..., description="操作类型")
    checked_at: datetime | None = Field(None, description="校验时间")


class StatusCheckResponse(BaseModel):
    """账户状态校验 - 响应"""
    account_type: str
    account_id: str
    status: str
    allowed: bool
    reason: str | None
