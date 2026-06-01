from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.application import AccountApplication
from app.schemas.application import (
    AccountApplicationApprove,
    AccountApplicationCreate,
    AccountApplicationRead,
    AccountApplicationReject,
    ApprovalRecordRead,
)
from app.schemas.common import ApiResponse, ok
from app.services import application_service

router = APIRouter(prefix="/applications")


@router.post(
    "",
    response_model=ApiResponse[AccountApplicationRead],
    status_code=status.HTTP_201_CREATED,
)
def create_application(
    payload: AccountApplicationCreate,
    db: Session = Depends(get_db),
) -> ApiResponse[AccountApplicationRead]:
    application = application_service.submit_application(db, payload)
    return ok(AccountApplicationRead.model_validate(application), "开户申请提交成功")


@router.get("", response_model=ApiResponse[list[AccountApplicationRead]])
def list_applications(
    app_status: str | None = Query(None),
    proc_status: str | None = Query(None),
    db: Session = Depends(get_db),
) -> ApiResponse[list[AccountApplicationRead]]:
    applications = application_service.list_applications(db, app_status, proc_status)
    return ok([AccountApplicationRead.model_validate(item) for item in applications])


@router.get("/{application_id}", response_model=ApiResponse[AccountApplicationRead])
def get_application(
    application_id: str,
    db: Session = Depends(get_db),
) -> ApiResponse[AccountApplicationRead]:
    application = db.get(AccountApplication, application_id)
    if not application:
        from fastapi import HTTPException

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="开户申请不存在")
    return ok(AccountApplicationRead.model_validate(application))


@router.post("/{application_id}/approve", response_model=ApiResponse[AccountApplicationRead])
def approve_application(
    application_id: str,
    payload: AccountApplicationApprove,
    db: Session = Depends(get_db),
) -> ApiResponse[AccountApplicationRead]:
    application = application_service.approve_application(
        db,
        application_id,
        payload.approver_id,
        payload.approval_opinion,
    )
    return ok(AccountApplicationRead.model_validate(application), "审批通过，已生成连续开户结果")


@router.post("/{application_id}/reject", response_model=ApiResponse[AccountApplicationRead])
def reject_application(
    application_id: str,
    payload: AccountApplicationReject,
    db: Session = Depends(get_db),
) -> ApiResponse[AccountApplicationRead]:
    application = application_service.reject_application(
        db,
        application_id,
        payload.approver_id,
        payload.approval_opinion,
    )
    return ok(AccountApplicationRead.model_validate(application), "审批拒绝")


@router.get(
    "/{application_id}/approval-records",
    response_model=ApiResponse[list[ApprovalRecordRead]],
)
def get_approval_records(
    application_id: str,
    db: Session = Depends(get_db),
) -> ApiResponse[list[ApprovalRecordRead]]:
    records = application_service.list_approval_records(db, application_id)
    return ok([ApprovalRecordRead.model_validate(record) for record in records])
