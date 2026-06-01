from datetime import datetime

from pydantic import BaseModel, Field

from app.core.enums import CustomerStatus, StaffRole, StaffStatus
from app.schemas.common import OrmModel


class CustomerCreate(BaseModel):
    customer_id: str = Field(..., examples=["CUST000001"])
    customer_name: str
    id_number: str
    phone: str
    customer_status: CustomerStatus = CustomerStatus.ACTIVE


class CustomerRead(OrmModel):
    customer_id: str
    customer_name: str
    id_number: str
    phone: str
    customer_status: CustomerStatus
    created_at: datetime
    updated_at: datetime


class StaffCreate(BaseModel):
    staff_id: str = Field(..., examples=["STAFF000001"])
    staff_name: str
    role: StaffRole = StaffRole.STAFF
    phone: str | None = None
    staff_status: StaffStatus = StaffStatus.ACTIVE


class StaffRead(OrmModel):
    staff_id: str
    staff_name: str
    role: StaffRole
    phone: str | None
    staff_status: StaffStatus
    created_at: datetime
    updated_at: datetime
