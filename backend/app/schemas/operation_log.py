from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import OrmModel


class OperationLogCreate(BaseModel):
    """操作日志 - 创建请求"""
    operator_id: str = Field(..., min_length=1, max_length=32, description="操作人员 ID")
    operator_name: str = Field(..., min_length=1, max_length=64, description="操作人员姓名")
    operation_type: str = Field(..., min_length=1, max_length=32, description="操作类型")
    target_type: str = Field(..., min_length=1, max_length=32, description="操作目标类型")
    target_id: str = Field(..., min_length=1, max_length=64, description="操作目标 ID")
    operation_detail: str | None = Field(None, description="操作详情")
    operation_result: str = Field("SUCCESS", min_length=1, max_length=16, description="操作结果")
    fail_reason: str | None = Field(None, description="失败原因")
    client_ip: str | None = Field(None, max_length=64, description="客户端 IP")
    request_id: str | None = Field(None, max_length=64, description="请求追踪 ID")


class OperationLogResponse(OrmModel):
    """操作日志 - 响应结构"""
    log_id: str
    operator_id: str
    operator_name: str
    operation_type: str
    target_type: str
    target_id: str
    operation_detail: str | None
    operation_result: str
    fail_reason: str | None
    client_ip: str | None
    request_id: str | None
    created_at: datetime
