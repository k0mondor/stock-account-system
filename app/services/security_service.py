"""证券账户业务逻辑"""

from sqlalchemy.orm import Session
from app.crud import security_account as security_account_crud
from app.utils.exceptions import (
    NotFoundException,
    InsufficientPositionException,
    AccountBlockedException,
)
from app.utils.constants import AccountStatus


def get_positions_info(
    db: Session,
    security_account_id: str,
    stock_code: str = None,
) -> dict:
    """获取证券持仓"""
    account = security_account_crud.get_security_account(db, security_account_id)
    if not account:
        raise NotFoundException(f"证券账户不存在: {security_account_id}")
    
    if account.status != AccountStatus.NORMAL:
        raise AccountBlockedException(f"账户状态异常: {account.status}")
    
    positions = security_account_crud.get_positions(
        db=db,
        security_account_id=security_account_id,
        stock_code=stock_code,
    )
    
    return {
        "security_account_id": security_account_id,
        "positions": [
            {
                "stock_code": pos.stock_code,
                "stock_name": pos.stock_name,
                "total_quantity": pos.total_quantity,
                "available_quantity": pos.available_quantity,
                "frozen_quantity": pos.frozen_quantity,
                "cost_price": str(pos.cost_price) if pos.cost_price else None,
            }
            for pos in positions
        ],
    }


def freeze_position(
    db: Session,
    security_account_id: str,
    freeze_id: str,
    position_id: str,
    order_id: str,
    stock_code: str,
    freeze_quantity: int,
    freeze_reason: str,
) -> dict:
    """冻结持仓"""
    account = security_account_crud.get_security_account(db, security_account_id)
    if not account:
        raise NotFoundException(f"证券账户不存在: {security_account_id}")
    
    if account.status != AccountStatus.NORMAL:
        raise AccountBlockedException(f"账户状态异常: {account.status}")
    
    try:
        freeze_record = security_account_crud.create_position_freeze(
            db=db,
            freeze_id=freeze_id,
            security_account_id=security_account_id,
            position_id=position_id,
            order_id=order_id,
            stock_code=stock_code,
            freeze_quantity=freeze_quantity,
            freeze_reason=freeze_reason,
        )
        
        # 获取更新后的持仓
        position = db.query(type(freeze_record).__bases__[0]).filter_by(
            position_id=position_id
        ).first()
        if not position:
            from app.models import SecurityPosition
            position = db.query(SecurityPosition).filter_by(
                position_id=position_id
            ).first()
        
        return {
            "freeze_id": freeze_record.freeze_id,
            "security_account_id": security_account_id,
            "stock_code": stock_code,
            "freeze_quantity": freeze_record.freeze_quantity,
            "available_quantity": position.available_quantity if position else 0,
            "created_at": freeze_record.created_at,
        }
    except ValueError as e:
        raise Exception(str(e))


def release_position(
    db: Session,
    security_account_id: str,
    order_id: str,
    release_reason: str,
) -> dict:
    """释放持仓"""
    account = security_account_crud.get_security_account(db, security_account_id)
    if not account:
        raise NotFoundException(f"证券账户不存在: {security_account_id}")
    
    success, message = security_account_crud.release_position_freeze(
        db=db,
        security_account_id=security_account_id,
        order_id=order_id,
        release_reason=release_reason,
    )
    
    if not success:
        raise Exception(message)
    
    return {
        "security_account_id": security_account_id,
        "success": True,
    }


def settlement_position(
    db: Session,
    security_account_id: str,
    settlement_id: str,
    position_id: str,
    message_id: str,
    stock_code: str,
    settlement_type: str,
    settlement_quantity: int,
    settlement_reason: str,
    order_id: str = None,
    trade_id: str = None,
) -> dict:
    """证券结算"""
    account = security_account_crud.get_security_account(db, security_account_id)
    if not account:
        raise NotFoundException(f"证券账户不存在: {security_account_id}")
    
    try:
        settlement = security_account_crud.create_position_settlement(
            db=db,
            settlement_id=settlement_id,
            security_account_id=security_account_id,
            position_id=position_id,
            message_id=message_id,
            stock_code=stock_code,
            settlement_type=settlement_type,
            settlement_quantity=settlement_quantity,
            settlement_reason=settlement_reason,
            order_id=order_id,
            trade_id=trade_id,
        )
        
        return {
            "settlement_id": settlement.settlement_id,
            "security_account_id": settlement.security_account_id,
            "stock_code": stock_code,
            "settlement_quantity": settlement.settlement_quantity,
            "settlement_type": settlement.settlement_type,
            "total_quantity_after": settlement.total_quantity_after,
            "available_quantity_after": settlement.available_quantity_after,
            "frozen_quantity_after": settlement.frozen_quantity_after,
        }
    except ValueError as e:
        raise Exception(str(e))
