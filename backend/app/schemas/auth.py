from datetime import datetime

from pydantic import BaseModel, Field

from app.core.enums import PasswordType


class LoginRequest(BaseModel):
    fund_account_id: str = Field(..., min_length=1, max_length=32)
    password: str = Field(..., min_length=1, max_length=64)
    client_time: datetime | None = None


class LoginResponse(BaseModel):
    verified: bool
    investor_id: str
    fund_account_id: str
    security_account_id: str
    first_login: bool = False
    token: str
    expires_at: datetime


class PasswordChangeRequest(BaseModel):
    fund_account_id: str = Field(..., min_length=1, max_length=32)
    password_type: PasswordType
    old_password: str = Field(..., min_length=1, max_length=64)
    new_password: str = Field(..., min_length=6, max_length=64)


class PasswordChangeResponse(BaseModel):
    fund_account_id: str
    password_type: PasswordType
    changed: bool
