from datetime import datetime, timezone
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic.generics import GenericModel

T = TypeVar("T")


class ApiResponse(GenericModel, Generic[T]):
    success: bool = True
    code: str = "OK"
    message: str = "success"
    data: T | None = None
    request_id: str | None = None
    timestamp: datetime


def ok(data: T | None = None, message: str = "success") -> ApiResponse[T]:
    return ApiResponse(data=data, message=message, timestamp=datetime.now(timezone.utc))


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
