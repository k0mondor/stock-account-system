"""资金账户业务逻辑"""

from decimal import Decimal
from sqlalchemy.orm import Session
from app.crud import fund_account as fund_account_crud
from app.models import FundAccount
from app.utils.exceptions import (
    NotFoundException,
    InsufficientFundsException,
    AccountBlockedException,
)
from app.utils.constants import AccountStatus


def get_fund_account_info(db: Session, fund_account_id: str) -> dict:
    """获取资金账户信息"""
    account = fund_account_crud.get_fund_account(db, fund_account_id)
    if not account:
        raise NotFoundException(f"资金账户不存在: {fund_account_id}")
    
    if account.status != AccountStatus.NORMAL:
        raise AccountBlockedException(f"账户状态异常: {account.status}")
    
    return {
        "fund_account_id": account.fund_account_id,
        "investor_id": account.investor_id,
        "available_amount": str(account.available_amount),
        "frozen_amount": str(account.frozen_amount),
        "total_amount": str(account.total_amount),
        "status": account.status.value,
    }


def freeze_fund(
    db: Session,
    fund_account_id: str,
    freeze_id: str,
    order_id: str,
    freeze_amount: Decimal,
    freeze_reason: str,
) -> dict:
    """冻结资金"""
    account = fund_account_crud.get_fund_account(db, fund_account_id)
    if not account:
        raise NotFoundException(f"资金账户不存在: {fund_account_id}")
    
    if account.status != AccountStatus.NORMAL:
        raise AccountBlockedException(f"账户状态异常: {account.status}")
    
    if account.available_amount < freeze_amount:
        raise InsufficientFundsException("可用资金不足")
    
    try:
        freeze_record = fund_account_crud.create_fund_freeze(
            db=db,
            freeze_id=freeze_id,
            fund_account_id=fund_account_id,
            order_id=order_id,
            freeze_amount=freeze_amount,
            freeze_reason=freeze_reason,
        )
        
        # 刷新账户
        db.refresh(account)
        
        return {
            "freeze_id": freeze_record.freeze_id,
            "fund_account_id": account.fund_account_id,
            "freeze_amount": str(freeze_record.freeze_amount),
            "available_amount": str(account.available_amount),
            "created_at": freeze_record.created_at,
        }
    except ValueError as e:
        raise Exception(str(e))


def release_fund(
    db: Session,
    fund_account_id: str,
    order_id: str,
    release_reason: str,
) -> dict:
    """释放资金"""
    account = fund_account_crud.get_fund_account(db, fund_account_id)
    if not account:
        raise NotFoundException(f"资金账户不存在: {fund_account_id}")
    
    success, message = fund_account_crud.release_fund_freeze(
        db=db,
        fund_account_id=fund_account_id,
        order_id=order_id,
        release_reason=release_reason,
    )
    
    if not success:
        raise Exception(message)
    
    # 刷新账户
    db.refresh(account)
    
    return {
        "fund_account_id": account.fund_account_id,
        "available_amount": str(account.available_amount),
    }


def settlement_fund(
    db: Session,
    fund_account_id: str,
    settlement_id: str,
    message_id: str,
    settlement_type: str,
    settlement_amount: Decimal,
    settlement_reason: str,
    order_id: str = None,
    trade_id: str = None,
) -> dict:
    """资金结算"""
    account = fund_account_crud.get_fund_account(db, fund_account_id)
    if not account:
        raise NotFoundException(f"资金账户不存在: {fund_account_id}")
    
    try:
        settlement = fund_account_crud.create_fund_settlement(
            db=db,
            settlement_id=settlement_id,
            fund_account_id=fund_account_id,
            message_id=message_id,
            settlement_type=settlement_type,
            settlement_amount=settlement_amount,
            settlement_reason=settlement_reason,
            order_id=order_id,
            trade_id=trade_id,
        )
        
        return {
            "settlement_id": settlement.settlement_id,
            "fund_account_id": settlement.fund_account_id,
            "settlement_amount": str(settlement.settlement_amount),
            "settlement_type": settlement.settlement_type,
            "available_amount_after": str(settlement.available_amount_after),
            "frozen_amount_after": str(settlement.frozen_amount_after),
            "total_amount_after": str(settlement.total_amount_after),
        }
    except ValueError as e:
        raise Exception(str(e))
