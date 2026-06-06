from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import AccountStatus, PositionChangeType
from app.models.security_account import SecuritiesAccount
from app.models.security_position import PositionTransactionRecord, SecurityPosition


def _new_id(prefix: str) -> str:
    return f"{prefix}{uuid4().hex[:18].upper()}"


def list_positions(
    db: Session,
    security_account_id: str,
    stock_code: str | None = None,
) -> list[SecurityPosition]:
    account = db.get(SecuritiesAccount, security_account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="证券账户不存在")
    query = select(SecurityPosition).where(
        SecurityPosition.security_account_id == security_account_id
    )
    if stock_code:
        query = query.where(SecurityPosition.stock_code == stock_code)
    return list(db.scalars(query.order_by(SecurityPosition.stock_code)).all())


def change_position(
    db: Session,
    *,
    security_account_id: str,
    business_order_id: str,
    stock_code: str,
    change_type: PositionChangeType,
    quantity: int,
    reason: str | None,
    trade_id: str | None = None,
    stock_name: str | None = None,
    cost_price: Decimal | None = None,
) -> tuple[SecurityPosition, PositionTransactionRecord]:
    from app.services.association_service import (
        require_active_association_for_security,
    )

    operation_type = {
        PositionChangeType.FREEZE: "SELL_ORDER",
        PositionChangeType.RELEASE: "CANCEL_ORDER",
        PositionChangeType.DEDUCT: "SETTLEMENT",
        PositionChangeType.INCREASE: "SETTLEMENT",
    }[change_type]
    require_active_association_for_security(
        db,
        security_account_id=security_account_id,
        operation_type=operation_type,
    )
    account = db.scalar(
        select(SecuritiesAccount)
        .where(SecuritiesAccount.security_account_id == security_account_id)
        .with_for_update()
    )
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="证券账户不存在")
    allowed_statuses = (
        {AccountStatus.NORMAL.value}
        if change_type == PositionChangeType.FREEZE
        else {AccountStatus.NORMAL.value, AccountStatus.FROZEN.value}
    )
    if account.account_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"证券账户状态为 {account.account_status}，不允许持仓变动",
        )

    existing_record = db.scalar(
        select(PositionTransactionRecord).where(
            PositionTransactionRecord.security_account_id == security_account_id,
            PositionTransactionRecord.business_order_id == business_order_id,
            PositionTransactionRecord.change_type == change_type.value,
            PositionTransactionRecord.stock_code == stock_code,
        )
    )
    if existing_record:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="业务订单已处理，请勿重复提交",
        )

    position = db.scalar(
        select(SecurityPosition)
        .where(
            SecurityPosition.security_account_id == security_account_id,
            SecurityPosition.stock_code == stock_code,
        )
        .with_for_update()
    )
    if not position:
        if change_type != PositionChangeType.INCREASE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="证券持仓不存在",
            )
        position = SecurityPosition(
            position_id=_new_id("POS"),
            security_account_id=security_account_id,
            investor_id=account.investor_id,
            stock_code=stock_code,
            stock_name=stock_name,
            cost_price=cost_price,
        )
        db.add(position)
        db.flush()

    if change_type == PositionChangeType.FREEZE:
        if position.available_quantity < quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="可用持仓不足",
            )
        position.available_quantity -= quantity
        position.frozen_quantity += quantity
    elif change_type == PositionChangeType.RELEASE:
        if position.frozen_quantity < quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="冻结持仓不足",
            )
        position.frozen_quantity -= quantity
        position.available_quantity += quantity
    elif change_type == PositionChangeType.DEDUCT:
        if position.frozen_quantity < quantity or position.total_quantity < quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="冻结持仓不足，无法结算扣减",
            )
        position.frozen_quantity -= quantity
        position.total_quantity -= quantity
    else:
        position.total_quantity += quantity
        position.available_quantity += quantity
        if stock_name:
            position.stock_name = stock_name
        if cost_price is not None:
            position.cost_price = cost_price

    record = PositionTransactionRecord(
        record_id=_new_id("PTR"),
        security_account_id=security_account_id,
        business_order_id=business_order_id,
        trade_id=trade_id,
        stock_code=stock_code,
        change_type=change_type.value,
        quantity=quantity,
        reason=reason,
    )
    db.add(record)
    db.flush()
    return position, record
