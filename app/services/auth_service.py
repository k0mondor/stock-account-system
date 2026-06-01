"""认证业务逻辑"""

from datetime import timedelta
from sqlalchemy.orm import Session
from app.crud import user as user_crud
from app.crud import fund_account as fund_account_crud
from app.crud import security_account as security_account_crud
from app.crud import association as association_crud
from app.utils.jwt_utils import create_access_token, verify_password
from app.utils.exceptions import AuthenticationException, NotFoundException


def authenticate_user(
    db: Session,
    investor_id: str,
    password: str,
) -> dict:
    """认证用户并返回登录信息"""
    # 查询用户
    user = user_crud.get_user_by_fund_account_id(db, investor_id)
    if not user:
        raise NotFoundException("用户不存在")
    
    # 验证密码
    if not verify_password(password, user.trade_password_hash):
        raise AuthenticationException("密码错误")
    
    # 获取资金账户和证券账户
    fund_account = fund_account_crud.get_fund_account_by_investor(db, investor_id)
    security_account = security_account_crud.get_security_account_by_investor(db, investor_id)
    
    if not fund_account or not security_account:
        raise NotFoundException("账户未初始化")
    
    # 创建token
    access_token_expires = timedelta(minutes=480)
    token_data = {
        "sub": investor_id,
        "fund_account_id": fund_account.fund_account_id,
        "security_account_id": security_account.security_account_id,
    }
    access_token = create_access_token(data=token_data, expires_delta=access_token_expires)
    
    return {
        "verified": True,
        "investor_id": investor_id,
        "fund_account_id": fund_account.fund_account_id,
        "security_account_id": security_account.security_account_id,
        "token": access_token,
        "token_type": "Bearer",
        "expires_at": None,  # 由FastAPI的token授权处理
    }


def change_password(
    db: Session,
    investor_id: str,
    old_password: str,
    new_password: str,
    password_type: str = "TRADE",
) -> bool:
    """修改用户密码"""
    # 查询用户
    user = user_crud.get_user_by_fund_account_id(db, investor_id)
    if not user:
        raise NotFoundException("用户不存在")
    
    # 验证原密码
    if not user_crud.verify_user_password(db, investor_id, old_password, password_type):
        raise AuthenticationException("原密码错误")
    
    # 更新密码
    success = user_crud.update_user_password(db, investor_id, new_password, password_type)
    if not success:
        raise Exception("密码修改失败")
    
    return True
