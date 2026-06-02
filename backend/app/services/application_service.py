from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import ApplicationStatus, ApprovalResult, ProcessStatus, StaffRole
from app.models.application import AccountApplication, ApprovalRecord
from app.models.base_data import Customer, Staff
from app.schemas.application import AccountApplicationCreate


def _new_id(prefix: str) -> str:
    return f"{prefix}{uuid4().hex[:18].upper()}"


def submit_application(db: Session, payload: AccountApplicationCreate) -> AccountApplication:
    customer = db.get(Customer, payload.customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="客户不存在")

    existing = db.scalars(
        select(AccountApplication).where(
            AccountApplication.customer_id == payload.customer_id,
            AccountApplication.app_status == ApplicationStatus.SUBMITTED.value,
            AccountApplication.proc_status.in_(
                [ProcessStatus.PENDING.value, ProcessStatus.APPROVED.value]
            ),
        )
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="客户已有待处理开户申请")

    application = AccountApplication(
        application_id=_new_id("APP"),
        customer_id=payload.customer_id,
        applicant_name=payload.applicant_name,
        id_number=payload.id_number,
        phone=payload.phone,
        remark=payload.remark,
        app_status=ApplicationStatus.SUBMITTED.value,
        proc_status=ProcessStatus.PENDING.value,
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def approve_application(
    db: Session,
    application_id: str,
    approver_id: str,
    approval_opinion: str | None,
) -> AccountApplication:
    application = db.get(AccountApplication, application_id)
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="开户申请不存在")
    if application.proc_status != ProcessStatus.PENDING.value:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="开户申请状态不允许审批")

    approver = db.get(Staff, approver_id)
    if not approver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="审批人员不存在")
    if approver.role not in {StaffRole.APPROVER.value, StaffRole.ADMIN.value}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="当前工作人员无审批权限")

    now = datetime.utcnow()
    application.proc_status = ProcessStatus.COMPLETED.value
    application.processed_at = now
    application.fund_account_id = _new_id("FUND")
    application.security_account_id = _new_id("SEC")

    record = ApprovalRecord(
        approval_id=_new_id("APR"),
        application_id=application.application_id,
        approver_id=approver_id,
        approval_result=ApprovalResult.APPROVED.value,
        approval_opinion=approval_opinion,
        approved_at=now,
    )
    db.add(record)
    db.commit()
    db.refresh(application)
    return application


def reject_application(
    db: Session,
    application_id: str,
    approver_id: str,
    approval_opinion: str,
) -> AccountApplication:
    application = db.get(AccountApplication, application_id)
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="开户申请不存在")
    if application.proc_status != ProcessStatus.PENDING.value:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="开户申请状态不允许审批")

    approver = db.get(Staff, approver_id)
    if not approver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="审批人员不存在")
    if approver.role not in {StaffRole.APPROVER.value, StaffRole.ADMIN.value}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="当前工作人员无审批权限")

    now = datetime.utcnow()
    application.proc_status = ProcessStatus.REJECTED.value
    application.processed_at = now

    record = ApprovalRecord(
        approval_id=_new_id("APR"),
        application_id=application.application_id,
        approver_id=approver_id,
        approval_result=ApprovalResult.REJECTED.value,
        approval_opinion=approval_opinion,
        approved_at=now,
    )
    db.add(record)
    db.commit()
    db.refresh(application)
    return application


def list_applications(
    db: Session,
    app_status: str | None = None,
    proc_status: str | None = None,
) -> list[AccountApplication]:
    query = select(AccountApplication).order_by(AccountApplication.created_at.desc())
    if app_status:
        query = query.where(AccountApplication.app_status == app_status)
    if proc_status:
        query = query.where(AccountApplication.proc_status == proc_status)
    return list(db.scalars(query).all())


def list_approval_records(db: Session, application_id: str) -> list[ApprovalRecord]:
    application = db.get(AccountApplication, application_id)
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="开户申请不存在")

    return list(
        db.scalars(
            select(ApprovalRecord)
            .where(ApprovalRecord.application_id == application_id)
            .order_by(ApprovalRecord.created_at.asc())
        ).all()
    )
