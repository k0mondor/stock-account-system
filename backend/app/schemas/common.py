import uuid
from datetime import datetime, timezone
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一 HTTP 响应包装结构"""
    success: bool = True
    code: str = "OK"
    message: str = "success"
    data: T | None = None
    request_id: str | None = None
    timestamp: datetime

    @classmethod
    def ok(cls, data: T | None = None, message: str = "success") -> "ApiResponse[T]":
        return cls(
            success=True,
            code="OK",
            message=message,
            data=data,
            request_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
        )

    @classmethod
    def error(cls, code: str, message: str) -> "ApiResponse[None]":
        return cls(
            success=False,
            code=code,
            message=message,
            data=None,
            request_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
        )


class OrmModel(BaseModel):
    """SQLAlchemy 模型转 Pydantic 用的配置 Mixin"""
    model_config = ConfigDict(from_attributes=True)


# 兼容旧代码的快捷函数
def ok(data=None, message="success"):
    return ApiResponse.ok(data=data, message=message)
