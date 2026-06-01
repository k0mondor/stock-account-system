"""认证相关的Pydantic Schema"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求"""
    fund_account_id: str = Field(..., description="资金账户号")
    password: str = Field(..., description="登录密码（交易密码）")
    client_time: datetime = Field(..., description="客户端时间")


class LoginResponse(BaseModel):
    """登录响应"""
    verified: bool = Field(..., description="是否验证成功")
    investor_id: str = Field(..., description="投资者编号")
    fund_account_id: str = Field(..., description="资金账户号")
    security_account_id: str = Field(..., description="证券账户号")
    token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="Bearer", description="令牌类型")
    expires_at: datetime = Field(..., description="令牌过期时间")


class PasswordChangeRequest(BaseModel):
    """密码修改请求"""
    fund_account_id: str = Field(..., description="资金账户号")
    password_type: str = Field(..., description="密码类型: TRADE 或 WITHDRAW")
    old_password: str = Field(..., description="原密码")
    new_password: str = Field(..., description="新密码")


class PasswordChangeResponse(BaseModel):
    """密码修改响应"""
    success: bool = Field(..., description="是否修改成功")
    fund_account_id: str = Field(..., description="资金账户号")
    password_type: str = Field(..., description="修改的密码类型")
    changed_at: datetime = Field(..., description="修改时间")


class TokenPayload(BaseModel):
    """令牌payload"""
    sub: str  # investor_id
    fund_account_id: str
    security_account_id: str
    exp: Optional[datetime] = None
