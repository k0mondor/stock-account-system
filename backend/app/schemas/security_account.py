from datetime import datetime

from pydantic import BaseModel, Field

from app.core.enums import AccountStatus
from app.schemas.common import OrmModel


class SecuritiesAccountResponse(OrmModel):
    security_account_id: str
    investor_id: str
    account_status: AccountStatus
    created_at: datetime
    updated_at: datetime


class SecurityPasswordResetRequest(BaseModel):
    staff_id: str = Field(..., min_length=1, max_length=32)
    customer_id_number: str = Field(..., min_length=1, max_length=32)
    new_password: str = Field(..., min_length=6, max_length=64)
    reason: str = Field(..., min_length=1, max_length=256)


class SecurityPasswordResetResponse(BaseModel):
    security_account_id: str
    changed: bool
