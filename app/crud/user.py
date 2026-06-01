"""用户数据访问层"""

from sqlalchemy.orm import Session
from app.models import InvestorUser, OperationLog
from app.utils.jwt_utils import get_password_hash, verify_password


def create_user(
    db: Session,
    investor_id: str,
    username: str,
    real_name: str,
    id_card: str,
    phone: str,
    email: str,
    trade_password: str,
    withdraw_password: str,
) -> InvestorUser:
    """创建用户"""
    db_user = InvestorUser(
        investor_id=investor_id,
        username=username,
        real_name=real_name,
        id_card=id_card,
        phone=phone,
        email=email,
        trade_password_hash=get_password_hash(trade_password),
        withdraw_password_hash=get_password_hash(withdraw_password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_fund_account_id(db: Session, investor_id: str) -> InvestorUser | None:
    """通过投资者ID获取用户"""
    return db.query(InvestorUser).filter(
        InvestorUser.investor_id == investor_id,
        InvestorUser.is_active == True
    ).first()


def get_user_by_username(db: Session, username: str) -> InvestorUser | None:
    """通过用户名获取用户"""
    return db.query(InvestorUser).filter(
        InvestorUser.username == username,
        InvestorUser.is_active == True
    ).first()


def get_user_by_id_card(db: Session, id_card: str) -> InvestorUser | None:
    """通过身份证号获取用户"""
    return db.query(InvestorUser).filter(
        InvestorUser.id_card == id_card,
        InvestorUser.is_active == True,
    ).first()


def verify_user_password(
    db: Session,
    investor_id: str,
    password: str,
    password_type: str = "TRADE"
) -> bool:
    """验证用户密码"""
    user = get_user_by_fund_account_id(db, investor_id)
    if not user:
        return False
    
    if password_type == "TRADE":
        return verify_password(password, user.trade_password_hash)
    elif password_type == "WITHDRAW":
        return verify_password(password, user.withdraw_password_hash)
    return False


def update_user_password(
    db: Session,
    investor_id: str,
    new_password: str,
    password_type: str = "TRADE"
) -> bool:
    """更新用户密码"""
    user = get_user_by_fund_account_id(db, investor_id)
    if not user:
        return False
    
    if password_type == "TRADE":
        user.trade_password_hash = get_password_hash(new_password)
    elif password_type == "WITHDRAW":
        user.withdraw_password_hash = get_password_hash(new_password)
    else:
        return False
    
    db.commit()
    db.refresh(user)
    return True


def create_operation_log(
    db: Session,
    log_id: str,
    investor_id: str,
    operator: str,
    operation_type: str,
    object_type: str,
    object_id: str,
    action: str,
    description: str = None,
    old_value: str = None,
    new_value: str = None,
    is_success: bool = True,
    error_message: str = None,
    request_id: str = None,
    ip_address: str = None,
) -> OperationLog:
    """创建操作日志"""
    log = OperationLog(
        log_id=log_id,
        investor_id=investor_id,
        operator=operator,
        operation_type=operation_type,
        object_type=object_type,
        object_id=object_id,
        action=action,
        description=description,
        old_value=old_value,
        new_value=new_value,
        is_success=is_success,
        error_message=error_message,
        request_id=request_id,
        ip_address=ip_address,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
