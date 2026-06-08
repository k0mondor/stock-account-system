from decimal import Decimal

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.enums import AccountStatus, FundChangeType
from app.core.auth_dependencies import authorize_fund_account, require_service_token
from app.db.session import get_db
from app.models.fund_account import FundAccount
from app.schemas.common import ApiResponse
from app.schemas.fund_account import (
    AccountCloseRequest,
    AccountStateChangeRequest,
    FundAccountResponse,
    FundOperationRequest,
    FundSettlementRequest,
    FundTradeChangeRequest,
    FundTradeChangeResponse,
    FundTransactionResponse,
    FundWithdrawRequest,
    StaffPasswordResetRequest,
)
from app.schemas.auth import PasswordChangeResponse
from app.services import account_state_service, fund_account_service

router = APIRouter()


@router.get(
    "/{fund_account_id}",
    response_model=ApiResponse[FundAccountResponse],
    summary="查询资金账户",
    description="根据资金账户号查询账户详细信息。",
)
def get_fund_account(
    fund_account_id: str,
    claims: dict = Depends(authorize_fund_account),
    db: Session = Depends(get_db),
) -> ApiResponse[FundAccountResponse]:
    del claims
    """
    查询资金账户接口：

    - **fund_account_id**: 资金账户号

    返回账户的完整信息，包括余额、状态等。
    """
    fund_account = db.query(FundAccount).filter(
        FundAccount.fund_account_id == fund_account_id
    ).first()
    if not fund_account:
        raise HTTPException(
            status_code=404,
            detail=f"资金账户 {fund_account_id} 不存在",
        )

    return ApiResponse.ok(
        data=FundAccountResponse.model_validate(fund_account),
        message="查询成功",
    )


def _transaction_response(fund_account, transaction) -> FundTransactionResponse:
    return FundTransactionResponse(
        transaction_id=transaction.transaction_id,
        fund_account_id=transaction.fund_account_id,
        business_order_id=transaction.business_order_id,
        operator_staff_id=transaction.operator_staff_id,
        transaction_type=transaction.transaction_type,
        amount=transaction.amount,
        reason=transaction.reason,
        occurred_at=transaction.occurred_at,
        available_amount=fund_account.available_balance,
        frozen_amount=fund_account.frozen_amount,
        total_amount=fund_account.total_amount,
    )


@router.post(
    "/{fund_account_id}/deposits",
    response_model=ApiResponse[FundTransactionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="资金账户存款",
)
def deposit(
    fund_account_id: str,
    payload: FundOperationRequest,
    claims: dict = Depends(require_service_token),
    db: Session = Depends(get_db),
) -> ApiResponse[FundTransactionResponse]:
    del claims
    try:
        account, transaction = fund_account_service.deposit(
            db,
            fund_account_id,
            amount=payload.amount,
            business_order_id=payload.business_order_id,
            reason=payload.reason,
            operator_id=payload.operator_id,
            operator_name=payload.operator_name,
        )
        db.commit()
        db.refresh(account)
        db.refresh(transaction)
    except Exception:
        db.rollback()
        raise
    return ApiResponse.ok(
        data=_transaction_response(account, transaction),
        message="存款成功",
    )


@router.post(
    "/{fund_account_id}/withdrawals",
    response_model=ApiResponse[FundTransactionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="资金账户取款",
)
def withdraw(
    fund_account_id: str,
    payload: FundWithdrawRequest,
    claims: dict = Depends(require_service_token),
    db: Session = Depends(get_db),
) -> ApiResponse[FundTransactionResponse]:
    del claims
    try:
        account, transaction = fund_account_service.withdraw(
            db,
            fund_account_id,
            amount=payload.amount,
            withdraw_password=payload.withdraw_password,
            business_order_id=payload.business_order_id,
            reason=payload.reason,
            operator_id=payload.operator_id,
            operator_name=payload.operator_name,
        )
        db.commit()
        db.refresh(account)
        db.refresh(transaction)
    except Exception:
        db.rollback()
        raise
    return ApiResponse.ok(
        data=_transaction_response(account, transaction),
        message="取款成功",
    )


@router.post(
    "/{fund_account_id}/password/reset",
    response_model=ApiResponse[PasswordChangeResponse],
    summary="工作人员代理重置资金账户密码",
    description="内部柜台业务：校验工作人员权限和客户身份后重置指定类型密码。",
)
def reset_password_by_staff(
    fund_account_id: str,
    payload: StaffPasswordResetRequest,
    claims: dict = Depends(require_service_token),
    db: Session = Depends(get_db),
) -> ApiResponse[PasswordChangeResponse]:
    del claims
    try:
        fund_account_service.reset_password_by_staff(
            db,
            fund_account_id,
            staff_id=payload.staff_id,
            customer_id_number=payload.customer_id_number,
            password_type=payload.password_type,
            new_password=payload.new_password,
            reason=payload.reason,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return ApiResponse.ok(
        PasswordChangeResponse(
            fund_account_id=fund_account_id,
            password_type=payload.password_type,
            changed=True,
        ),
        "密码重置成功",
    )


@router.delete(
    "/{fund_account_id}",
    response_model=ApiResponse[FundAccountResponse],
    summary="禁止单独资金销户",
)
def close_fund_account(
    fund_account_id: str,
    payload: AccountCloseRequest = Body(...),
    claims: dict = Depends(require_service_token),
    db: Session = Depends(get_db),
) -> ApiResponse[FundAccountResponse]:
    del claims
    del db, fund_account_id, payload
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="请使用联合销户接口",
    )


@router.get(
    "/{fund_account_id}/transactions",
    response_model=ApiResponse[dict],
    summary="查询资金流水",
)
def list_transactions(
    fund_account_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    claims: dict = Depends(require_service_token),
    db: Session = Depends(get_db),
) -> ApiResponse[dict]:
    del claims
    records, total = fund_account_service.list_transactions(
        db,
        fund_account_id,
        page=page,
        page_size=page_size,
    )
    return ApiResponse.ok(
        {
            "items": [
                {
                    "transaction_id": item.transaction_id,
                    "fund_account_id": item.fund_account_id,
                    "business_order_id": item.business_order_id,
                    "transaction_type": item.transaction_type,
                    "amount": item.amount,
                    "reason": item.reason,
                    "occurred_at": item.occurred_at,
                }
                for item in records
            ],
            "page": page,
            "page_size": page_size,
            "total": total,
        },
        "查询成功",
    )


def _trade_change_response(account, transaction) -> FundTradeChangeResponse:
    return FundTradeChangeResponse(
        transaction_id=transaction.transaction_id,
        fund_account_id=account.fund_account_id,
        business_order_id=transaction.business_order_id,
        change_type=transaction.transaction_type,
        changed_amount=transaction.amount,
        available_amount=account.available_balance,
        frozen_amount=account.frozen_amount,
        total_amount=account.total_amount,
    )


def _apply_trade_change(
    db: Session,
    fund_account_id: str,
    *,
    change_type: FundChangeType,
    amount: Decimal,
    business_order_id: str,
    reason: str | None,
) -> ApiResponse[FundTradeChangeResponse]:
    try:
        account, transaction = fund_account_service.change_trade_funds(
            db,
            fund_account_id,
            change_type=change_type,
            amount=amount,
            business_order_id=business_order_id,
            reason=reason,
        )
        db.commit()
        db.refresh(account)
        db.refresh(transaction)
    except Exception:
        db.rollback()
        raise
    return ApiResponse.ok(_trade_change_response(account, transaction), "资金变动成功")


@router.post(
    "/{fund_account_id}/freeze",
    response_model=ApiResponse[FundTradeChangeResponse],
    summary="冻结交易资金",
)
def freeze_funds(
    fund_account_id: str,
    payload: FundTradeChangeRequest,
    claims: dict = Depends(authorize_fund_account),
    db: Session = Depends(get_db),
) -> ApiResponse[FundTradeChangeResponse]:
    del claims
    return _apply_trade_change(
        db,
        fund_account_id,
        change_type=FundChangeType.FREEZE,
        amount=payload.amount,
        business_order_id=payload.order_id,
        reason=payload.reason,
    )


@router.post(
    "/{fund_account_id}/release",
    response_model=ApiResponse[FundTradeChangeResponse],
    summary="释放交易资金",
)
def release_funds(
    fund_account_id: str,
    payload: FundTradeChangeRequest,
    claims: dict = Depends(authorize_fund_account),
    db: Session = Depends(get_db),
) -> ApiResponse[FundTradeChangeResponse]:
    del claims
    return _apply_trade_change(
        db,
        fund_account_id,
        change_type=FundChangeType.RELEASE,
        amount=payload.amount,
        business_order_id=payload.order_id,
        reason=payload.reason,
    )


@router.post(
    "/{fund_account_id}/settlements",
    response_model=ApiResponse[FundTradeChangeResponse],
    summary="资金结算",
)
def settle_funds(
    fund_account_id: str,
    payload: FundSettlementRequest,
    claims: dict = Depends(authorize_fund_account),
    db: Session = Depends(get_db),
) -> ApiResponse[FundTradeChangeResponse]:
    del claims
    return _apply_trade_change(
        db,
        fund_account_id,
        change_type=payload.change_type,
        amount=payload.amount,
        business_order_id=payload.message_id,
        reason=f"order={payload.order_id}; trade={payload.trade_id}; {payload.reason or ''}",
    )


def _change_fund_status(
    db: Session,
    fund_account_id: str,
    target_status: AccountStatus,
    payload: AccountStateChangeRequest,
) -> ApiResponse[FundAccountResponse]:
    try:
        account = account_state_service.change_status(
            db,
            account_type="FUND",
            account_id=fund_account_id,
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
    return ApiResponse.ok(FundAccountResponse.model_validate(account))


@router.post(
    "/{fund_account_id}/lost",
    response_model=ApiResponse[FundAccountResponse],
    summary="资金账户挂失",
)
def report_fund_account_lost(
    fund_account_id: str,
    payload: AccountStateChangeRequest,
    claims: dict = Depends(require_service_token),
    db: Session = Depends(get_db),
) -> ApiResponse[FundAccountResponse]:
    del claims
    return _change_fund_status(db, fund_account_id, AccountStatus.LOST, payload)


@router.post(
    "/{fund_account_id}/reissue",
    response_model=ApiResponse[FundAccountResponse],
    summary="资金账户挂失补办",
)
def reissue_fund_account(
    fund_account_id: str,
    payload: AccountStateChangeRequest,
    claims: dict = Depends(require_service_token),
    db: Session = Depends(get_db),
) -> ApiResponse[FundAccountResponse]:
    del claims
    return _change_fund_status(db, fund_account_id, AccountStatus.NORMAL, payload)
