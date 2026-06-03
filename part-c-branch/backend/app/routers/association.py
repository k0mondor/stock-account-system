from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.fund_account import FundAccount
from app.schemas.association import (
    AssociationCheckResponse,
    AssociationResponse,
)
from app.schemas.common import ApiResponse
from app.services import association_service
from app.core.enums import AccountStatus

router = APIRouter()


@router.get(
    "",
    response_model=ApiResponse[AssociationResponse],
    summary="账户关联查询",
    description="根据资金账户号、证券账户号或投资者编号查询账户关联关系。",
)
def query_association(
    fund_account_id: str | None = Query(None, description="资金账户号"),
    security_account_id: str | None = Query(None, description="证券账户号"),
    investor_id: str | None = Query(None, description="投资者编号"),
    db: Session = Depends(get_db),
) -> ApiResponse[AssociationResponse]:
    if not fund_account_id and not security_account_id and not investor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="至少需要提供一个查询条件：fund_account_id、security_account_id 或 investor_id",
        )

    association = association_service.get_association(
        db,
        fund_account_id=fund_account_id,
        security_account_id=security_account_id,
        investor_id=investor_id,
    )

    if not association:
        return ApiResponse.ok(
            data=AssociationResponse(
                association_id=None,
                investor_id=investor_id or "UNKNOWN",
                fund_account_id=fund_account_id or "",
                security_account_id=security_account_id or "",
                association_status="UNLINKED",
                associated_at=None,
            ),
            message="未找到有效关联关系",
        )

    return ApiResponse.ok(
        data=AssociationResponse.model_validate(association),
        message="查询成功",
    )


@router.get(
    "/check",
    response_model=ApiResponse[AssociationCheckResponse],
    summary="账户关联业务校验",
    description="校验证券账户与资金账户是否满足一对一绑定，并判断当前业务是否允许继续。",
)
def check_association(
    fund_account_id: str = Query(..., description="资金账户号"),
    security_account_id: str = Query(..., description="证券账户号"),
    operation_type: str = Query(..., description="当前业务类型"),
    investor_id: str | None = Query(None, description="投资者编号"),
    db: Session = Depends(get_db),
) -> ApiResponse[AssociationCheckResponse]:
    result = association_service.check_association(
        db,
        fund_account_id=fund_account_id,
        security_account_id=security_account_id,
        operation_type=operation_type,
        investor_id=investor_id,
    )
    return ApiResponse.ok(
        data=AssociationCheckResponse(**result),
        message="校验完成",
    )


@router.post(
    "",
    response_model=ApiResponse[AssociationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="创建账户关联",
    description="创建资金账户与证券账户的一对一绑定关系。",
)
def create_association(
    investor_id: str = Query(..., description="投资者编号"),
    fund_account_id: str = Query(..., description="资金账户号"),
    security_account_id: str = Query(..., description="证券账户号"),
    db: Session = Depends(get_db),
) -> ApiResponse[AssociationResponse]:
    fund_account = db.get(FundAccount, fund_account_id)
    if not fund_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"资金账户 {fund_account_id} 不存在",
        )
    if fund_account.account_status != AccountStatus.NORMAL.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="资金账户状态异常，无法建立关联",
        )

    association = association_service.create_association(
        db,
        investor_id=investor_id,
        fund_account_id=fund_account_id,
        security_account_id=security_account_id,
    )
    db.commit()
    db.refresh(association)
    return ApiResponse.ok(
        data=AssociationResponse.model_validate(association),
        message="关联创建成功",
    )


@router.delete(
    "",
    response_model=ApiResponse[AssociationResponse],
    summary="解除账户关联",
    description="解除资金账户与证券账户的绑定关系。",
)
def unlink_association(
    fund_account_id: str | None = Query(None, description="资金账户号"),
    security_account_id: str | None = Query(None, description="证券账户号"),
    db: Session = Depends(get_db),
) -> ApiResponse[AssociationResponse]:
    if not fund_account_id and not security_account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="至少需要提供 fund_account_id 或 security_account_id",
        )

    association = association_service.unlink_association(
        db,
        fund_account_id=fund_account_id,
        security_account_id=security_account_id,
    )
    db.commit()
    db.refresh(association)
    return ApiResponse.ok(
        data=AssociationResponse.model_validate(association),
        message="关联已解除",
    )
