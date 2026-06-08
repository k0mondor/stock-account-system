from datetime import datetime

from pydantic import BaseModel, Field

from app.core.enums import AccountStatus, AssociationStatus


class JointAccountCloseRequest(BaseModel):
    fund_account_id: str = Field(..., min_length=1, max_length=32)
    security_account_id: str = Field(..., min_length=1, max_length=32)
    customer_id_number: str = Field(..., min_length=1, max_length=32)
    operator_id: str = Field(..., min_length=1, max_length=32)
    operator_name: str = Field(..., min_length=1, max_length=64)
    reason: str | None = Field(None, max_length=256)


class JointAccountCloseResponse(BaseModel):
    association_id: str
    investor_id: str
    fund_account_id: str
    security_account_id: str
    association_status: AssociationStatus
    fund_account_status: AccountStatus
    security_account_status: AccountStatus
    closed_at: datetime
