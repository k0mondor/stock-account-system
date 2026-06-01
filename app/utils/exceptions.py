"""自定义异常"""

from fastapi import HTTPException, status


class AccountException(HTTPException):
    """账户系统基础异常"""
    pass


class AuthenticationException(AccountException):
    """认证异常"""
    def __init__(self, detail: str = "认证失败"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class UnauthorizedException(AccountException):
    """未授权异常"""
    def __init__(self, detail: str = "未授权"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class NotFoundException(AccountException):
    """资源不存在异常"""
    def __init__(self, detail: str = "资源不存在"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class BadRequestException(AccountException):
    """请求格式错误异常"""
    def __init__(self, detail: str = "请求格式错误"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class ConflictException(AccountException):
    """资源状态冲突异常"""
    def __init__(self, detail: str = "资源状态冲突"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class InsufficientFundsException(AccountException):
    """资金不足异常"""
    def __init__(self, detail: str = "可用资金不足"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class InsufficientPositionException(AccountException):
    """持仓不足异常"""
    def __init__(self, detail: str = "可用持仓不足"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class AccountBlockedException(AccountException):
    """账户被冻结异常"""
    def __init__(self, detail: str = "账户状态不允许当前操作"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
