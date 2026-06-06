from datetime import datetime

from pydantic import BaseModel, Field

from app.core.enums import ApplicationStatus, ApprovalResult, ProcessStatus
from app.schemas.common import OrmModel


class AccountApplicationCreate(BaseModel):
    customer_id: str = Field(..., min_length=1, max_length=32, examples=["CUST000001"])
    applicant_name: str = Field(..., min_length=1, max_length=64)
    id_number: str = Field(..., min_length=1, max_length=32)
    phone: str = Field(..., min_length=1, max_length=20)
    remark: str | None = Field(None, max_length=1000)


class AccountApplicationRead(OrmModel):
    application_id: str
    customer_id: str
    applicant_name: str
    id_number: str
    phone: str
    app_status: ApplicationStatus
    proc_status: ProcessStatus
    fund_account_id: str | None
    security_account_id: str | None
    submitted_at: datetime
    processed_at: datetime | None
    remark: str | None
    created_at: datetime
    updated_at: datetime


class AccountApplicationApprove(BaseModel):
    approver_id: str = Field(..., examples=["APR000001"])
    approval_opinion: str | None = Field(None, max_length=1000)
    bank_card_no: str = Field(..., min_length=8, max_length=32)
    trade_password: str = Field(..., min_length=6, max_length=64)
    withdraw_password: str = Field(..., min_length=6, max_length=64)


class AccountApplicationReject(BaseModel):
    approver_id: str = Field(..., examples=["APR000001"])
    approval_opinion: str = Field(..., min_length=1, max_length=1000)


class ApprovalRecordRead(OrmModel):
    approval_id: str
    application_id: str
    approver_id: str
    approval_result: ApprovalResult
    approval_opinion: str | None
    approved_at: datetime
    created_at: datetime
