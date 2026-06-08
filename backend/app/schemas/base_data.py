from datetime import datetime

from pydantic import BaseModel, Field

from app.core.enums import CustomerStatus, StaffRole, StaffStatus
from app.schemas.common import OrmModel


class CustomerCreate(BaseModel):
    customer_id: str = Field(..., min_length=1, max_length=32, examples=["CUST000001"])
    customer_name: str = Field(..., min_length=1, max_length=64)
    id_type: str = Field("ID_CARD", min_length=1, max_length=32)
    id_number: str = Field(..., min_length=1, max_length=32)
    phone: str = Field(..., min_length=1, max_length=20)
    gender: str = Field(..., min_length=1, max_length=16)
    address: str = Field(..., min_length=1, max_length=255)
    occupation: str = Field(..., min_length=1, max_length=64)
    education_level: str = Field(..., min_length=1, max_length=32)
    employer: str = Field(..., min_length=1, max_length=128)
    agent_id_number: str | None = Field(None, max_length=32)
    customer_status: CustomerStatus = CustomerStatus.ACTIVE


class CustomerUpdate(BaseModel):
    customer_name: str | None = Field(None, min_length=1, max_length=64)
    phone: str | None = Field(None, min_length=1, max_length=20)
    id_type: str | None = Field(None, min_length=1, max_length=32)
    gender: str | None = Field(None, min_length=1, max_length=16)
    address: str | None = Field(None, min_length=1, max_length=255)
    occupation: str | None = Field(None, min_length=1, max_length=64)
    education_level: str | None = Field(None, min_length=1, max_length=32)
    employer: str | None = Field(None, min_length=1, max_length=128)
    agent_id_number: str | None = Field(None, max_length=32)
    customer_status: CustomerStatus | None = None


class CustomerRead(OrmModel):
    customer_id: str
    customer_name: str
    id_type: str | None
    id_number: str
    phone: str
    gender: str | None
    address: str | None
    occupation: str | None
    education_level: str | None
    employer: str | None
    agent_id_number: str | None
    customer_status: CustomerStatus
    created_at: datetime
    updated_at: datetime


class StaffCreate(BaseModel):
    staff_id: str = Field(..., min_length=1, max_length=32, examples=["STAFF000001"])
    staff_name: str = Field(..., min_length=1, max_length=64)
    role: StaffRole = StaffRole.STAFF
    phone: str | None = Field(None, max_length=20)
    staff_status: StaffStatus = StaffStatus.ACTIVE


class StaffRead(OrmModel):
    staff_id: str
    staff_name: str
    role: StaffRole
    phone: str | None
    staff_status: StaffStatus
    created_at: datetime
    updated_at: datetime
