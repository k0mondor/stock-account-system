from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.auth_dependencies import require_access_token, require_service_token
from app.core.account_rules import allowed_statuses
from app.schemas.association import (
    AssociationCheckResponse,
    AssociationHistoryResponse,
    AssociationResponse,
)
from app.schemas.common import ApiResponse
from app.services import association_service

router = APIRouter()


@router.get(
    "/history",
    response_model=ApiResponse[list[AssociationHistoryResponse]],
    summary="查询账户关联历史",
    description="查询当前有效及已解除的绑定记录，用于业务办理历史追踪。",
)
def query_association_history(
    fund_account_id: str | None = Query(None, description="资金账户号"),
    security_account_id: str | None = Query(None, description="证券账户号"),
    investor_id: str | None = Query(None, description="投资者编号"),
    claims: dict = Depends(require_service_token),
    db: Session = Depends(get_db),
) -> ApiResponse[list[AssociationHistoryResponse]]:
    del claims
    if not fund_account_id and not security_account_id and not investor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="至少需要提供一个查询条件：fund_account_id、security_account_id 或 investor_id",
        )
    records = association_service.list_association_history(
        db,
        fund_account_id=fund_account_id,
        security_account_id=security_account_id,
        investor_id=investor_id,
    )
    return ApiResponse.ok(
        [AssociationHistoryResponse.model_validate(item) for item in records],
        "查询成功",
    )


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
    claims: dict = Depends(require_access_token),
    db: Session = Depends(get_db),
) -> ApiResponse[AssociationResponse]:
    if not fund_account_id and not security_account_id and not investor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="至少需要提供一个查询条件：fund_account_id、security_account_id 或 investor_id",
        )
    if claims["token_type"] != "SERVICE":
        if fund_account_id and claims["fund_account_id"] != fund_account_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="访问令牌与资金账户不匹配",
            )
        if (
            security_account_id
            and claims["security_account_id"] != security_account_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="访问令牌与证券账户不匹配",
            )
        if investor_id and claims["investor_id"] != investor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="访问令牌与投资者不匹配",
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
                disassociated_at=None,
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
    claims: dict = Depends(require_access_token),
    db: Session = Depends(get_db),
) -> ApiResponse[AssociationCheckResponse]:
    if claims["token_type"] != "SERVICE" and (
        claims["fund_account_id"] != fund_account_id
        or claims["security_account_id"] != security_account_id
        or (investor_id and claims["investor_id"] != investor_id)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="访问令牌与待校验账户不匹配",
        )
    if allowed_statuses(operation_type) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的业务类型: {operation_type}",
        )
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
    claims: dict = Depends(require_service_token),
    db: Session = Depends(get_db),
) -> ApiResponse[AssociationResponse]:
    del claims
    try:
        association = association_service.create_association(
            db,
            investor_id=investor_id,
            fund_account_id=fund_account_id,
            security_account_id=security_account_id,
        )
        db.commit()
        db.refresh(association)
    except Exception:
        db.rollback()
        raise
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
    claims: dict = Depends(require_service_token),
    db: Session = Depends(get_db),
) -> ApiResponse[AssociationResponse]:
    del claims
    if not fund_account_id and not security_account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="至少需要提供 fund_account_id 或 security_account_id",
        )

    try:
        association = association_service.unlink_association(
            db,
            fund_account_id=fund_account_id,
            security_account_id=security_account_id,
        )
        db.commit()
        db.refresh(association)
    except Exception:
        db.rollback()
        raise
    return ApiResponse.ok(
        data=AssociationResponse.model_validate(association),
        message="关联已解除",
    )
