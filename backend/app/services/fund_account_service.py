from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import (
    AccountStatus,
    AssociationStatus,
    FundChangeType,
    PasswordType,
    StaffRole,
    StaffStatus,
)
from app.core.security import hash_password, verify_password
from app.core.time import utc_now
from app.models.association import AccountAssociation
from app.models.base_data import Customer, Staff
from app.models.fund_account import FundAccount
from app.models.fund_account import FundTransactionRecord
from app.services.account_state_service import record_status_change
from app.services.operation_log_service import add_operation_log


def _new_id(prefix: str) -> str:
    return f"{prefix}{uuid4().hex[:18].upper()}"


def create_fund_account(
    db: Session,
    fund_account_id: str,
    investor_id: str,
    bank_card_no: str,
    trade_password: str,
    withdraw_password: str,
) -> FundAccount:
    """
    创建资金账户（供联合开户流程调用，不作为独立外部接口）。

    - **fund_account_id**: 资金账户号
    - **investor_id**: 投资者编号
    - **bank_card_no**: 绑定的银行卡号

    账户创建时可用资金、冻结资金、总资金均初始化为 0，账户状态默认为 NORMAL。
    """
    fund_account = FundAccount(
        fund_account_id=fund_account_id,
        investor_id=investor_id,
        bank_card_no=bank_card_no,
        trade_password_hash=hash_password(trade_password),
        withdraw_password_hash=hash_password(withdraw_password),
    )
    db.add(fund_account)
    db.flush()
    return fund_account


def _get_normal_account_for_update(db: Session, fund_account_id: str) -> FundAccount:
    account = db.scalar(
        select(FundAccount)
        .where(FundAccount.fund_account_id == fund_account_id)
        .with_for_update()
    )
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="资金账户不存在")
    if account.account_status != AccountStatus.NORMAL.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"资金账户状态为 {account.account_status}，不允许执行资金操作",
        )
    return account


def _record_transaction(
    db: Session,
    account: FundAccount,
    *,
    transaction_type: str,
    amount: Decimal,
    business_order_id: str | None,
    operator_staff_id: str | None,
    reason: str | None,
) -> FundTransactionRecord:
    if business_order_id:
        existing = db.scalar(
            select(FundTransactionRecord).where(
                FundTransactionRecord.fund_account_id == account.fund_account_id,
                FundTransactionRecord.business_order_id == business_order_id,
                FundTransactionRecord.transaction_type == transaction_type,
            )
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="业务订单已处理，请勿重复提交",
            )

    record = FundTransactionRecord(
        transaction_id=_new_id("TXN"),
        fund_account_id=account.fund_account_id,
        business_order_id=business_order_id,
        operator_staff_id=operator_staff_id,
        transaction_type=transaction_type,
        amount=amount,
        reason=reason,
    )
    db.add(record)
    db.flush()
    return record


def _ensure_new_business_order(
    db: Session,
    account: FundAccount,
    *,
    business_order_id: str | None,
    transaction_type: str,
) -> None:
    if not business_order_id:
        return
    existing = db.scalar(
        select(FundTransactionRecord).where(
            FundTransactionRecord.fund_account_id == account.fund_account_id,
            FundTransactionRecord.business_order_id == business_order_id,
            FundTransactionRecord.transaction_type == transaction_type,
        )
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="业务订单已处理，请勿重复提交",
        )


def deposit(
    db: Session,
    fund_account_id: str,
    *,
    amount: Decimal,
    business_order_id: str | None,
    reason: str | None,
    operator_id: str,
    operator_name: str,
) -> tuple[FundAccount, FundTransactionRecord]:
    account = _get_normal_account_for_update(db, fund_account_id)
    _ensure_new_business_order(
        db,
        account,
        business_order_id=business_order_id,
        transaction_type="DEPOSIT",
    )
    account.available_balance += amount
    account.total_amount += amount
    record = _record_transaction(
        db,
        account,
        transaction_type="DEPOSIT",
        amount=amount,
        business_order_id=business_order_id,
        operator_staff_id=operator_id,
        reason=reason or "柜台存款",
    )
    add_operation_log(
        db,
        operator_id=operator_id,
        operator_name=operator_name,
        operation_type="DEPOSIT",
        target_type="FUND",
        target_id=fund_account_id,
        operation_detail=f"资金账户存款 {amount:.2f}",
    )
    db.flush()
    return account, record


def withdraw(
    db: Session,
    fund_account_id: str,
    *,
    amount: Decimal,
    withdraw_password: str,
    business_order_id: str | None,
    reason: str | None,
    operator_id: str,
    operator_name: str,
) -> tuple[FundAccount, FundTransactionRecord]:
    account = _get_normal_account_for_update(db, fund_account_id)
    _ensure_new_business_order(
        db,
        account,
        business_order_id=business_order_id,
        transaction_type="WITHDRAW",
    )
    if not verify_password(withdraw_password, account.withdraw_password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="取款密码错误",
        )
    if account.available_balance < amount:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="可用余额不足",
        )

    account.available_balance -= amount
    account.total_amount -= amount
    record = _record_transaction(
        db,
        account,
        transaction_type="WITHDRAW",
        amount=amount,
        business_order_id=business_order_id,
        operator_staff_id=operator_id,
        reason=reason or "柜台取款",
    )
    add_operation_log(
        db,
        operator_id=operator_id,
        operator_name=operator_name,
        operation_type="WITHDRAW",
        target_type="FUND",
        target_id=fund_account_id,
        operation_detail=f"资金账户取款 {amount:.2f}",
    )
    db.flush()
    return account, record


def reset_password_by_staff(
    db: Session,
    fund_account_id: str,
    *,
    staff_id: str,
    customer_id_number: str,
    password_type: PasswordType,
    new_password: str,
    reason: str,
) -> FundAccount:
    account = _get_normal_account_for_update(db, fund_account_id)
    staff = db.get(Staff, staff_id)
    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="工作人员不存在")
    if staff.staff_status != StaffStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="工作人员状态不可用",
        )
    if staff.role not in {StaffRole.STAFF.value, StaffRole.ADMIN.value}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="当前工作人员无密码重置权限",
        )

    customer = db.get(Customer, account.investor_id)
    if not customer or customer.id_number != customer_id_number:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="客户身份信息与资金账户不匹配",
        )

    new_hash = hash_password(new_password)
    if password_type == PasswordType.TRADE:
        account.trade_password_hash = new_hash
    else:
        account.withdraw_password_hash = new_hash
    add_operation_log(
        db,
        operator_id=staff.staff_id,
        operator_name=staff.staff_name,
        operation_type="RESET_PASSWORD",
        target_type="FUND",
        target_id=fund_account_id,
        operation_detail=f"代理重置{password_type.value}密码，原因：{reason}",
    )
    db.flush()
    return account


def close_fund_account(
    db: Session,
    fund_account_id: str,
    *,
    customer_id_number: str,
    operator_id: str,
    operator_name: str,
) -> FundAccount:
    account = _get_normal_account_for_update(db, fund_account_id)
    customer = db.get(Customer, account.investor_id)
    if not customer or customer.id_number != customer_id_number:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="客户身份信息与资金账户不匹配",
        )
    zero = Decimal("0.00")
    if (
        account.available_balance != zero
        or account.frozen_amount != zero
        or account.total_amount != zero
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="账户资金不为 0，不能注销",
        )

    associations = list(db.scalars(
        select(AccountAssociation).where(
            AccountAssociation.fund_account_id == fund_account_id,
            AccountAssociation.association_status == AssociationStatus.ACTIVE.value,
        )
    ).all())
    if len(associations) > 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="资金账户存在多个有效绑定，请先修复关联数据",
        )
    for association in associations:
        association.association_status = AssociationStatus.UNLINKED.value
        now = utc_now()
        association.disassociated_at = now
        association.updated_at = now

    previous_status = account.account_status
    account.account_status = AccountStatus.CLOSED.value
    record_status_change(
        db,
        account_type="FUND",
        account_id=fund_account_id,
        previous_status=previous_status,
        target_status=AccountStatus.CLOSED.value,
        reason="资金账户销户",
        operator_id=operator_id,
        operator_name=operator_name,
        log_operation=False,
    )
    add_operation_log(
        db,
        operator_id=operator_id,
        operator_name=operator_name,
        operation_type="CLOSE_FUND_ACCOUNT",
        target_type="FUND",
        target_id=fund_account_id,
        operation_detail="注销资金账户并解除当前有效绑定关系",
    )
    db.flush()
    return account


def list_transactions(
    db: Session,
    fund_account_id: str,
    *,
    page: int,
    page_size: int,
) -> tuple[list[FundTransactionRecord], int]:
    from sqlalchemy import func

    if not db.get(FundAccount, fund_account_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="资金账户不存在")
    total = db.scalar(
        select(func.count()).select_from(FundTransactionRecord).where(
            FundTransactionRecord.fund_account_id == fund_account_id
        )
    ) or 0
    records = list(
        db.scalars(
            select(FundTransactionRecord)
            .where(FundTransactionRecord.fund_account_id == fund_account_id)
            .order_by(FundTransactionRecord.occurred_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
    )
    return records, total


def change_trade_funds(
    db: Session,
    fund_account_id: str,
    *,
    change_type: FundChangeType,
    amount: Decimal,
    business_order_id: str,
    reason: str | None,
) -> tuple[FundAccount, FundTransactionRecord]:
    from app.services.association_service import require_active_association_for_fund

    operation_type = {
        FundChangeType.FREEZE: "BUY_ORDER",
        FundChangeType.RELEASE: "CANCEL_ORDER",
        FundChangeType.DEDUCT: "SETTLEMENT",
        FundChangeType.INCREASE: "SETTLEMENT",
    }[change_type]
    require_active_association_for_fund(
        db,
        fund_account_id=fund_account_id,
        operation_type=operation_type,
    )
    account = db.scalar(
        select(FundAccount)
        .where(FundAccount.fund_account_id == fund_account_id)
        .with_for_update()
    )
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="资金账户不存在")
    allowed = (
        {AccountStatus.NORMAL.value}
        if change_type == FundChangeType.FREEZE
        else {AccountStatus.NORMAL.value, AccountStatus.FROZEN.value}
    )
    if account.account_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"资金账户状态为 {account.account_status}，不允许资金变动",
        )
    _ensure_new_business_order(
        db,
        account,
        business_order_id=business_order_id,
        transaction_type=change_type.value,
    )

    if change_type == FundChangeType.FREEZE:
        if account.available_balance < amount:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="可用资金不足",
            )
        account.available_balance -= amount
        account.frozen_amount += amount
    elif change_type == FundChangeType.RELEASE:
        if account.frozen_amount < amount:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="冻结资金不足",
            )
        account.frozen_amount -= amount
        account.available_balance += amount
    elif change_type == FundChangeType.DEDUCT:
        if account.frozen_amount < amount or account.total_amount < amount:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="冻结资金不足，无法结算扣减",
            )
        account.frozen_amount -= amount
        account.total_amount -= amount
    else:
        account.available_balance += amount
        account.total_amount += amount

    record = _record_transaction(
        db,
        account,
        transaction_type=change_type.value,
        amount=amount,
        business_order_id=business_order_id,
        operator_staff_id=None,
        reason=reason,
    )
    add_operation_log(
        db,
        operator_id="TRADE",
        operator_name="股票中央交易系统",
        operation_type=f"FUND_{change_type.value}",
        target_type="FUND",
        target_id=fund_account_id,
        operation_detail=f"{change_type.value} 资金 {amount:.2f}",
    )
    db.flush()
    return account, record
