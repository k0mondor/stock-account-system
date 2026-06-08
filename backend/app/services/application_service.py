from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import (
    AccountStatus,
    ApplicationStatus,
    ApprovalResult,
    AssociationStatus,
    CustomerStatus,
    ProcessStatus,
    StaffRole,
    StaffStatus,
)
from app.core.time import utc_now
from app.models.application import AccountApplication, ApprovalRecord
from app.models.association import AccountAssociation
from app.models.base_data import Customer, Staff
from app.models.fund_account import FundAccount
from app.models.security_account import SecuritiesAccount
from app.schemas.application import AccountApplicationCreate
from app.services import association_service, fund_account_service, security_account_service
from app.services.operation_log_service import add_operation_log


def _new_id(prefix: str) -> str:
    return f"{prefix}{uuid4().hex[:18].upper()}"


def validate_joint_open_preconditions(db: Session, customer_id: str) -> None:
    active_association = db.scalars(
        select(AccountAssociation).where(
            AccountAssociation.investor_id == customer_id,
            AccountAssociation.association_status == AssociationStatus.ACTIVE.value,
        )
    ).first()
    if active_association:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该客户已有当前有效的证券账户与资金账户绑定",
        )

    active_fund = db.scalars(
        select(FundAccount).where(
            FundAccount.investor_id == customer_id,
            FundAccount.account_status != AccountStatus.CLOSED.value,
        )
    ).first()
    active_security = db.scalars(
        select(SecuritiesAccount).where(
            SecuritiesAccount.investor_id == customer_id,
            SecuritiesAccount.account_status != AccountStatus.CLOSED.value,
        )
    ).first()
    if active_fund or active_security:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该客户已存在未注销账户，不能重复联合开户",
        )


def submit_application(db: Session, payload: AccountApplicationCreate) -> AccountApplication:
    customer = db.scalar(
        select(Customer)
        .where(Customer.customer_id == payload.customer_id)
        .with_for_update()
    )
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="客户不存在")
    if customer.customer_status != CustomerStatus.ACTIVE.value:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="客户状态不可用")
    if (
        payload.applicant_name != customer.customer_name
        or payload.id_number != customer.id_number
        or payload.phone != customer.phone
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="开户申请信息与客户档案不一致",
        )

    existing = db.scalars(
        select(AccountApplication).where(
            AccountApplication.customer_id == payload.customer_id,
            AccountApplication.app_status == ApplicationStatus.SUBMITTED.value,
            AccountApplication.proc_status == ProcessStatus.PENDING.value,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="客户已有待处理开户申请")
    validate_joint_open_preconditions(db, payload.customer_id)

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
    try:
        db.add(application)
        db.commit()
        db.refresh(application)
        return application
    except Exception:
        db.rollback()
        raise


def approve_application(
    db: Session,
    application_id: str,
    approver_id: str,
    approval_opinion: str | None,
    bank_card_no: str,
    trade_password: str,
    withdraw_password: str,
) -> AccountApplication:
    application = db.scalar(
        select(AccountApplication)
        .where(AccountApplication.application_id == application_id)
        .with_for_update()
    )
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="开户申请不存在")
    if application.proc_status != ProcessStatus.PENDING.value:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="开户申请状态不允许审批")

    customer = db.scalar(
        select(Customer)
        .where(Customer.customer_id == application.customer_id)
        .with_for_update()
    )
    if not customer:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="开户客户档案不存在")
    if customer.customer_status != CustomerStatus.ACTIVE.value:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="客户状态不可用")

    approver = db.get(Staff, approver_id)
    if not approver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="审批人员不存在")
    if approver.staff_status != StaffStatus.ACTIVE.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="审批人员状态不可用")
    if approver.role not in {StaffRole.APPROVER.value, StaffRole.ADMIN.value}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="当前工作人员无审批权限")

    validate_joint_open_preconditions(db, application.customer_id)

    now = utc_now()
    fund_account_id = _new_id("FUND")
    security_account_id = _new_id("SEC")

    try:
        security_account_service.create_security_account(
            db,
            security_account_id=security_account_id,
            investor_id=application.customer_id,
            security_password=trade_password,
        )
        fund_account_service.create_fund_account(
            db,
            fund_account_id=fund_account_id,
            investor_id=application.customer_id,
            bank_card_no=bank_card_no,
            trade_password=trade_password,
            withdraw_password=withdraw_password,
        )
        association_service.create_association(
            db,
            investor_id=application.customer_id,
            fund_account_id=fund_account_id,
            security_account_id=security_account_id,
            log_operation=False,
        )

        application.proc_status = ProcessStatus.COMPLETED.value
        application.processed_at = now
        application.fund_account_id = fund_account_id
        application.security_account_id = security_account_id

        record = ApprovalRecord(
            approval_id=_new_id("APR"),
            application_id=application.application_id,
            approver_id=approver_id,
            approval_result=ApprovalResult.APPROVED.value,
            approval_opinion=approval_opinion,
            approved_at=now,
        )
        db.add(record)
        add_operation_log(
            db,
            operator_id=approver.staff_id,
            operator_name=approver.staff_name,
            operation_type="JOINT_OPEN",
            target_type="APPLICATION",
            target_id=application.application_id,
            operation_detail=(
                f"联合创建证券账户 {security_account_id}、资金账户 "
                f"{fund_account_id} 并建立一对一绑定"
            ),
        )
        db.commit()
        db.refresh(application)
        return application
    except Exception:
        db.rollback()
        raise


def reject_application(
    db: Session,
    application_id: str,
    approver_id: str,
    approval_opinion: str,
) -> AccountApplication:
    application = db.scalar(
        select(AccountApplication)
        .where(AccountApplication.application_id == application_id)
        .with_for_update()
    )
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="开户申请不存在")
    if application.proc_status != ProcessStatus.PENDING.value:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="开户申请状态不允许审批")

    approver = db.get(Staff, approver_id)
    if not approver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="审批人员不存在")
    if approver.staff_status != StaffStatus.ACTIVE.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="审批人员状态不可用")
    if approver.role not in {StaffRole.APPROVER.value, StaffRole.ADMIN.value}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="当前工作人员无审批权限")

    now = utc_now()
    try:
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
        add_operation_log(
            db,
            operator_id=approver.staff_id,
            operator_name=approver.staff_name,
            operation_type="REJECT_APPLICATION",
            target_type="APPLICATION",
            target_id=application.application_id,
            operation_detail="拒绝开户申请",
        )
        db.commit()
        db.refresh(application)
        return application
    except Exception:
        db.rollback()
        raise


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
