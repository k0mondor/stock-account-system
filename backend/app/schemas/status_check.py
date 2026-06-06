from datetime import datetime

from pydantic import BaseModel, Field

from app.core.enums import AccountStatus
from app.schemas.common import OrmModel


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


class StatusHistoryResponse(OrmModel):
    change_id: str
    account_type: str
    account_id: str
    previous_status: AccountStatus
    target_status: AccountStatus
    reason: str | None
    operator_id: str
    operator_name: str
    changed_at: datetime


class StatusChangeRequest(BaseModel):
    account_type: str = Field(..., description="账户类型: FUND / SECURITY")
    account_id: str = Field(..., min_length=1, max_length=32)
    target_status: AccountStatus
    reason: str | None = Field(None, max_length=256)
    operator_id: str = Field("SYSTEM", min_length=1, max_length=32)
    operator_name: str = Field("系统", min_length=1, max_length=64)
