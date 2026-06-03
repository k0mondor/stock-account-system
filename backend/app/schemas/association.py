from datetime import datetime

from pydantic import BaseModel, Field

from app.core.enums import AssociationStatus
from app.schemas.common import OrmModel


class AssociationResponse(OrmModel):
    """账户关联 - 响应结构"""
    association_id: str | None
    investor_id: str
    fund_account_id: str
    security_account_id: str
    association_status: AssociationStatus
    associated_at: datetime | None


class AssociationCheckQuery(BaseModel):
    """账户关联业务校验 - 查询参数"""
    fund_account_id: str = Field(..., description="资金账户号")
    security_account_id: str = Field(..., description="证券账户号")
    operation_type: str = Field(..., description="当前业务类型")
    investor_id: str | None = Field(None, description="投资者编号")


class AssociationCheckResponse(BaseModel):
    """账户关联业务校验 - 响应结构"""
    fund_account_id: str
    security_account_id: str
    investor_id: str
    is_related: bool
    is_unique_valid: bool
    allow_operation: bool
    fund_account_status: str
    security_account_status: str
    reason: str | None
