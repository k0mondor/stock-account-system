from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.enums import AccountStatus, PositionChangeType
from app.core.auth_dependencies import (
    authorize_security_account,
    require_service_token,
)
from app.schemas.common import ApiResponse
from app.schemas.fund_account import AccountCloseRequest, AccountStateChangeRequest
from app.schemas.security_account import SecuritiesAccountResponse
from app.schemas.security_position import (
    PositionChangeRequest,
    PositionChangeResponse,
    PositionSettlementRequest,
    SecurityPositionListResponse,
    SecurityPositionResponse,
)
from app.services import (
    account_state_service,
    security_account_service,
    security_position_service,
)


router = APIRouter()


@router.get(
    "",
    response_model=ApiResponse[list[SecuritiesAccountResponse]],
    summary="查询证券账户列表",
)
def list_security_accounts(
    investor_id: str | None = Query(None),
    account_status: AccountStatus | None = Query(None),
    claims: dict = Depends(require_service_token),
    db: Session = Depends(get_db),
) -> ApiResponse[list[SecuritiesAccountResponse]]:
    del claims
    accounts = security_account_service.list_security_accounts(
        db,
        investor_id=investor_id,
        account_status=account_status.value if account_status else None,
    )
    return ApiResponse.ok(
        data=[SecuritiesAccountResponse.model_validate(item) for item in accounts],
        message="查询成功",
    )


@router.get(
    "/{security_account_id}",
    response_model=ApiResponse[SecuritiesAccountResponse],
    summary="查询证券账户",
)
def get_security_account(
    security_account_id: str,
    claims: dict = Depends(authorize_security_account),
    db: Session = Depends(get_db),
) -> ApiResponse[SecuritiesAccountResponse]:
    del claims
    account = security_account_service.get_security_account(db, security_account_id)
    return ApiResponse.ok(
        data=SecuritiesAccountResponse.model_validate(account),
        message="查询成功",
    )


@router.delete(
    "/{security_account_id}",
    response_model=ApiResponse[SecuritiesAccountResponse],
    summary="禁止单独证券销户",
)
def close_security_account(
    security_account_id: str,
    payload: AccountCloseRequest = Body(...),
    claims: dict = Depends(require_service_token),
    db: Session = Depends(get_db),
) -> ApiResponse[SecuritiesAccountResponse]:
    del claims
    del db, security_account_id, payload
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="请使用联合销户接口",
    )


@router.get(
    "/{security_account_id}/positions",
    response_model=ApiResponse[SecurityPositionListResponse],
    summary="查询证券持仓",
)
def list_positions(
    security_account_id: str,
    stock_code: str | None = Query(None, pattern=r"^\d{6}$"),
    claims: dict = Depends(authorize_security_account),
    db: Session = Depends(get_db),
) -> ApiResponse[SecurityPositionListResponse]:
    del claims
    positions = security_position_service.list_positions(
        db, security_account_id, stock_code
    )
    return ApiResponse.ok(
        SecurityPositionListResponse(
            security_account_id=security_account_id,
            positions=[
                SecurityPositionResponse.model_validate(item) for item in positions
            ],
        ),
        "查询成功",
    )


def _position_response(position, record) -> PositionChangeResponse:
    return PositionChangeResponse(
        record_id=record.record_id,
        security_account_id=position.security_account_id,
        business_order_id=record.business_order_id,
        stock_code=position.stock_code,
        change_type=record.change_type,
        changed_quantity=record.quantity,
        total_quantity=position.total_quantity,
        available_quantity=position.available_quantity,
        frozen_quantity=position.frozen_quantity,
    )


def _change_position(
    db: Session,
    security_account_id: str,
    **kwargs,
) -> ApiResponse[PositionChangeResponse]:
    try:
        position, record = security_position_service.change_position(
            db, security_account_id=security_account_id, **kwargs
        )
        db.commit()
        db.refresh(position)
        db.refresh(record)
    except Exception:
        db.rollback()
        raise
    return ApiResponse.ok(_position_response(position, record), "持仓变动成功")


@router.post(
    "/{security_account_id}/positions/freeze",
    response_model=ApiResponse[PositionChangeResponse],
    summary="冻结证券持仓",
)
def freeze_position(
    security_account_id: str,
    payload: PositionChangeRequest,
    claims: dict = Depends(authorize_security_account),
    db: Session = Depends(get_db),
) -> ApiResponse[PositionChangeResponse]:
    del claims
    return _change_position(
        db,
        security_account_id,
        business_order_id=payload.order_id,
        stock_code=payload.stock_code,
        change_type=PositionChangeType.FREEZE,
        quantity=payload.quantity,
        reason=payload.reason,
    )


@router.post(
    "/{security_account_id}/positions/release",
    response_model=ApiResponse[PositionChangeResponse],
    summary="释放证券持仓",
)
def release_position(
    security_account_id: str,
    payload: PositionChangeRequest,
    claims: dict = Depends(authorize_security_account),
    db: Session = Depends(get_db),
) -> ApiResponse[PositionChangeResponse]:
    del claims
    return _change_position(
        db,
        security_account_id,
        business_order_id=payload.order_id,
        stock_code=payload.stock_code,
        change_type=PositionChangeType.RELEASE,
        quantity=payload.quantity,
        reason=payload.reason,
    )


@router.post(
    "/{security_account_id}/positions/settlements",
    response_model=ApiResponse[PositionChangeResponse],
    summary="证券持仓结算",
)
def settle_position(
    security_account_id: str,
    payload: PositionSettlementRequest,
    claims: dict = Depends(authorize_security_account),
    db: Session = Depends(get_db),
) -> ApiResponse[PositionChangeResponse]:
    del claims
    return _change_position(
        db,
        security_account_id,
        business_order_id=payload.message_id,
        trade_id=payload.trade_id,
        stock_code=payload.stock_code,
        change_type=payload.change_type,
        quantity=payload.quantity,
        reason=f"order={payload.order_id}; {payload.reason or ''}",
        stock_name=payload.stock_name,
        cost_price=payload.cost_price,
    )


def _change_security_status(
    db: Session,
    security_account_id: str,
    target_status: AccountStatus,
    payload: AccountStateChangeRequest,
) -> ApiResponse[SecuritiesAccountResponse]:
    try:
        account = account_state_service.change_status(
            db,
            account_type="SECURITY",
            account_id=security_account_id,
            target_status=target_status,
            customer_id_number=payload.customer_id_number,
            reason=payload.reason,
            operator_id=payload.operator_id,
            operator_name=payload.operator_name,
        )
        db.commit()
        db.refresh(account)
    except Exception:
        db.rollback()
        raise
    return ApiResponse.ok(SecuritiesAccountResponse.model_validate(account))


@router.post(
    "/{security_account_id}/lost",
    response_model=ApiResponse[SecuritiesAccountResponse],
    summary="证券账户挂失",
)
def report_security_account_lost(
    security_account_id: str,
    payload: AccountStateChangeRequest,
    claims: dict = Depends(require_service_token),
    db: Session = Depends(get_db),
) -> ApiResponse[SecuritiesAccountResponse]:
    del claims
    return _change_security_status(
        db, security_account_id, AccountStatus.LOST, payload
    )


@router.post(
    "/{security_account_id}/reissue",
    response_model=ApiResponse[SecuritiesAccountResponse],
    summary="证券账户挂失补办",
)
def reissue_security_account(
    security_account_id: str,
    payload: AccountStateChangeRequest,
    claims: dict = Depends(require_service_token),
    db: Session = Depends(get_db),
) -> ApiResponse[SecuritiesAccountResponse]:
    del claims
    return _change_security_status(
        db, security_account_id, AccountStatus.NORMAL, payload
    )
