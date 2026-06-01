"""资金账户数据访问层"""

from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import FundAccount, FundFreeze, FundSettlement


def get_fund_account(db: Session, fund_account_id: str) -> FundAccount | None:
    """获取资金账户"""
    return db.query(FundAccount).filter(
        FundAccount.fund_account_id == fund_account_id
    ).first()


def create_fund_account(
    db: Session,
    fund_account_id: str,
    investor_id: str,
    bank_card_no: str = None,
    initial_amount: Decimal = Decimal("0.00"),
) -> FundAccount:
    """创建资金账户"""
    fund_account = FundAccount(
        fund_account_id=fund_account_id,
        investor_id=investor_id,
        bank_card_no=bank_card_no,
        available_amount=initial_amount,
        frozen_amount=Decimal("0.00"),
        total_amount=initial_amount,
    )
    db.add(fund_account)
    db.commit()
    db.refresh(fund_account)
    return fund_account


def create_fund_freeze(
    db: Session,
    freeze_id: str,
    fund_account_id: str,
    order_id: str,
    freeze_amount: Decimal,
    freeze_reason: str,
    message_id: str = None,
) -> FundFreeze:
    """创建资金冻结记录并更新账户余额"""
    # 获取账户
    fund_account = get_fund_account(db, fund_account_id)
    if not fund_account:
        raise ValueError(f"资金账户不存在: {fund_account_id}")
    
    # 检查可用资金
    if fund_account.available_amount < freeze_amount:
        raise ValueError("可用资金不足")
    
    # 更新账户
    fund_account.available_amount -= freeze_amount
    fund_account.frozen_amount += freeze_amount
    
    # 创建冻结记录
    freeze = FundFreeze(
        freeze_id=freeze_id,
        fund_account_id=fund_account_id,
        order_id=order_id,
        message_id=message_id,
        freeze_amount=freeze_amount,
        freeze_reason=freeze_reason,
    )
    db.add(freeze)
    db.commit()
    db.refresh(freeze)
    return freeze


def release_fund_freeze(
    db: Session,
    fund_account_id: str,
    order_id: str,
    release_reason: str,
) -> tuple[bool, str]:
    """释放资金冻结"""
    # 查找未释放的冻结记录
    freeze = db.query(FundFreeze).filter(
        and_(
            FundFreeze.fund_account_id == fund_account_id,
            FundFreeze.order_id == order_id,
            FundFreeze.is_released == False,
        )
    ).first()
    
    if not freeze:
        return False, "冻结记录不存在或已释放"
    
    # 获取账户
    fund_account = get_fund_account(db, fund_account_id)
    if not fund_account:
        return False, "资金账户不存在"
    
    # 更新账户
    fund_account.available_amount += freeze.freeze_amount
    fund_account.frozen_amount -= freeze.freeze_amount
    
    # 更新冻结记录
    freeze.is_released = True
    freeze.release_reason = release_reason
    
    db.commit()
    return True, "释放成功"


def create_fund_settlement(
    db: Session,
    settlement_id: str,
    fund_account_id: str,
    message_id: str,
    settlement_type: str,
    settlement_amount: Decimal,
    settlement_reason: str,
    order_id: str = None,
    trade_id: str = None,
) -> FundSettlement:
    """创建资金结算记录"""
    # 获取账户
    fund_account = get_fund_account(db, fund_account_id)
    if not fund_account:
        raise ValueError(f"资金账户不存在: {fund_account_id}")
    
    # 处理结算
    if settlement_type == "DEDUCT":
        if fund_account.available_amount < settlement_amount:
            raise ValueError("可用资金不足，无法结算")
        fund_account.available_amount -= settlement_amount
        fund_account.total_amount -= settlement_amount
    elif settlement_type == "INCREASE":
        fund_account.available_amount += settlement_amount
        fund_account.total_amount += settlement_amount
    else:
        raise ValueError(f"未知的结算类型: {settlement_type}")
    
    # 创建结算记录
    settlement = FundSettlement(
        settlement_id=settlement_id,
        fund_account_id=fund_account_id,
        message_id=message_id,
        order_id=order_id,
        trade_id=trade_id,
        settlement_type=settlement_type,
        settlement_amount=settlement_amount,
        settlement_reason=settlement_reason,
        available_amount_after=fund_account.available_amount,
        frozen_amount_after=fund_account.frozen_amount,
        total_amount_after=fund_account.total_amount,
    )
    db.add(settlement)
    db.commit()
    db.refresh(settlement)
    return settlement


def get_fund_freezes_by_order(
    db: Session,
    fund_account_id: str,
    order_id: str,
) -> list[FundFreeze]:
    """获取指令相关的冻结记录"""
    return db.query(FundFreeze).filter(
        and_(
            FundFreeze.fund_account_id == fund_account_id,
            FundFreeze.order_id == order_id,
        )
    ).all()


def get_fund_account_by_investor(
    db: Session,
    investor_id: str,
) -> FundAccount | None:
    """通过投资者ID获取资金账户"""
    return db.query(FundAccount).filter(
        FundAccount.investor_id == investor_id
    ).first()
