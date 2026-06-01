"""证券账户数据访问层"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import (
    SecurityAccount,
    SecurityPosition,
    PositionFreeze,
    PositionSettlement,
)


def get_security_account(db: Session, security_account_id: str) -> SecurityAccount | None:
    """获取证券账户"""
    return db.query(SecurityAccount).filter(
        SecurityAccount.security_account_id == security_account_id
    ).first()


def create_security_account(
    db: Session,
    security_account_id: str,
    investor_id: str,
) -> SecurityAccount:
    """创建证券账户"""
    security_account = SecurityAccount(
        security_account_id=security_account_id,
        investor_id=investor_id,
    )
    db.add(security_account)
    db.commit()
    db.refresh(security_account)
    return security_account


def get_positions(
    db: Session,
    security_account_id: str,
    stock_code: str = None,
) -> list[SecurityPosition]:
    """获取持仓列表"""
    query = db.query(SecurityPosition).filter(
        SecurityPosition.security_account_id == security_account_id
    )
    
    if stock_code:
        query = query.filter(SecurityPosition.stock_code == stock_code)
    
    return query.all()


def get_or_create_position(
    db: Session,
    position_id: str,
    security_account_id: str,
    investor_id: str,
    stock_code: str,
    stock_name: str = None,
) -> SecurityPosition:
    """获取或创建持仓"""
    position = db.query(SecurityPosition).filter(
        and_(
            SecurityPosition.security_account_id == security_account_id,
            SecurityPosition.stock_code == stock_code,
        )
    ).first()
    
    if not position:
        position = SecurityPosition(
            position_id=position_id,
            security_account_id=security_account_id,
            investor_id=investor_id,
            stock_code=stock_code,
            stock_name=stock_name,
        )
        db.add(position)
        db.commit()
        db.refresh(position)
    
    return position


def create_position_freeze(
    db: Session,
    freeze_id: str,
    security_account_id: str,
    position_id: str,
    order_id: str,
    stock_code: str,
    freeze_quantity: int,
    freeze_reason: str,
    message_id: str = None,
) -> PositionFreeze:
    """创建持仓冻结记录"""
    # 获取持仓
    position = db.query(SecurityPosition).filter(
        SecurityPosition.position_id == position_id
    ).first()
    
    if not position:
        raise ValueError(f"持仓不存在: {position_id}")
    
    # 检查可用数量
    if position.available_quantity < freeze_quantity:
        raise ValueError("可卖数量不足")
    
    # 更新持仓
    position.available_quantity -= freeze_quantity
    position.frozen_quantity += freeze_quantity
    
    # 创建冻结记录
    freeze = PositionFreeze(
        freeze_id=freeze_id,
        security_account_id=security_account_id,
        position_id=position_id,
        order_id=order_id,
        message_id=message_id,
        stock_code=stock_code,
        freeze_quantity=freeze_quantity,
        freeze_reason=freeze_reason,
    )
    db.add(freeze)
    db.commit()
    db.refresh(freeze)
    return freeze


def release_position_freeze(
    db: Session,
    security_account_id: str,
    order_id: str,
    release_reason: str,
) -> tuple[bool, str]:
    """释放持仓冻结"""
    # 查找未释放的冻结记录
    freeze = db.query(PositionFreeze).filter(
        and_(
            PositionFreeze.security_account_id == security_account_id,
            PositionFreeze.order_id == order_id,
            PositionFreeze.is_released == False,
        )
    ).first()
    
    if not freeze:
        return False, "冻结记录不存在或已释放"
    
    # 获取持仓
    position = db.query(SecurityPosition).filter(
        SecurityPosition.position_id == freeze.position_id
    ).first()
    
    if not position:
        return False, "持仓不存在"
    
    # 更新持仓
    position.available_quantity += freeze.freeze_quantity
    position.frozen_quantity -= freeze.freeze_quantity
    
    # 更新冻结记录
    freeze.is_released = True
    freeze.release_reason = release_reason
    
    db.commit()
    return True, "释放成功"


def create_position_settlement(
    db: Session,
    settlement_id: str,
    security_account_id: str,
    position_id: str,
    message_id: str,
    stock_code: str,
    settlement_type: str,
    settlement_quantity: int,
    settlement_reason: str,
    order_id: str = None,
    trade_id: str = None,
) -> PositionSettlement:
    """创建持仓结算记录"""
    # 获取持仓
    position = db.query(SecurityPosition).filter(
        SecurityPosition.position_id == position_id
    ).first()
    
    if not position:
        raise ValueError(f"持仓不存在: {position_id}")
    
    # 处理结算
    if settlement_type == "DEDUCT":
        if position.available_quantity < settlement_quantity:
            raise ValueError("可卖数量不足，无法结算")
        position.available_quantity -= settlement_quantity
        position.total_quantity -= settlement_quantity
    elif settlement_type == "INCREASE":
        position.available_quantity += settlement_quantity
        position.total_quantity += settlement_quantity
    else:
        raise ValueError(f"未知的结算类型: {settlement_type}")
    
    # 创建结算记录
    settlement = PositionSettlement(
        settlement_id=settlement_id,
        security_account_id=security_account_id,
        position_id=position_id,
        message_id=message_id,
        order_id=order_id,
        trade_id=trade_id,
        stock_code=stock_code,
        settlement_type=settlement_type,
        settlement_quantity=settlement_quantity,
        settlement_reason=settlement_reason,
        total_quantity_after=position.total_quantity,
        available_quantity_after=position.available_quantity,
        frozen_quantity_after=position.frozen_quantity,
    )
    db.add(settlement)
    db.commit()
    db.refresh(settlement)
    return settlement


def get_position_freezes_by_order(
    db: Session,
    security_account_id: str,
    order_id: str,
) -> list[PositionFreeze]:
    """获取指令相关的冻结记录"""
    return db.query(PositionFreeze).filter(
        and_(
            PositionFreeze.security_account_id == security_account_id,
            PositionFreeze.order_id == order_id,
        )
    ).all()


def get_security_account_by_investor(
    db: Session,
    investor_id: str,
) -> SecurityAccount | None:
    """通过投资者ID获取证券账户"""
    return db.query(SecurityAccount).filter(
        SecurityAccount.investor_id == investor_id
    ).first()
