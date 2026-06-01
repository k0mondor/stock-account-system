"""账户申请相关的Pydantic Schema"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class AccountApplicationSubmitRequest(BaseModel):
    """开户申请提交请求"""
    username: str = Field(..., min_length=3, max_length=100, description="用户名")
    real_name: str = Field(..., min_length=2, max_length=100, description="真实姓名")
    id_card: str = Field(..., description="身份证号")
    phone: str = Field(..., description="手机号码")
    email: str = Field(..., description="邮箱地址")


class AccountApplicationResponse(BaseModel):
    """开户申请响应"""
    application_id: str = Field(..., description="申请编号")
    investor_id: Optional[str] = Field(None, description="投资者编号")
    username: str = Field(..., description="用户名")
    real_name: str = Field(..., description="真实姓名")
    id_card: str = Field(..., description="身份证号")
    phone: str = Field(..., description="手机号码")
    email: str = Field(..., description="邮箱地址")
    status: str = Field(..., description="申请状态")
    fund_account_id: Optional[str] = Field(None, description="资金账户号")
    security_account_id: Optional[str] = Field(None, description="证券账户号")
    approval_reason: Optional[str] = Field(None, description="审批意见")
    approval_at: Optional[datetime] = Field(None, description="审批时间")
    created_at: datetime = Field(..., description="申请时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class ApplicationQueryRequest(BaseModel):
    """申请查询请求"""
    application_id: Optional[str] = Field(None, description="申请编号")
    username: Optional[str] = Field(None, description="用户名")
    id_card: Optional[str] = Field(None, description="身份证号")
    status: Optional[str] = Field(None, description="申请状态")


class ApprovalRequest(BaseModel):
    """审批请求"""
    application_id: str = Field(..., description="申请编号")
    approver_id: str = Field(..., description="审批人编号")
    approver_name: str = Field(..., description="审批人姓名")
    action: str = Field(..., description="审批操作：APPROVE/REJECT")
    reason: str = Field(..., description="审批意见")


class ApprovalResponse(BaseModel):
    """审批响应"""
    application_id: str = Field(..., description="申请编号")
    investor_id: Optional[str] = Field(None, description="投资者编号")
    status: str = Field(..., description="申请状态")
    fund_account_id: Optional[str] = Field(None, description="资金账户号")
    security_account_id: Optional[str] = Field(None, description="证券账户号")
    approval_reason: str = Field(..., description="审批意见")
    approval_at: datetime = Field(..., description="审批时间")


class ApprovalHistoryItem(BaseModel):
    """审批历史项"""
    history_id: str = Field(..., description="历史记录ID")
    action: str = Field(..., description="操作")
    action_by: str = Field(..., description="操作人编号")
    action_by_name: Optional[str] = Field(None, description="操作人名称")
    old_status: Optional[str] = Field(None, description="原状态")
    new_status: Optional[str] = Field(None, description="新状态")
    remark: Optional[str] = Field(None, description="备注")
    created_at: datetime = Field(..., description="操作时间")
    
    class Config:
        from_attributes = True


class ApprovalHistoryResponse(BaseModel):
    """审批历史响应"""
    application_id: str = Field(..., description="申请编号")
    histories: List[ApprovalHistoryItem] = Field(..., description="审批历史")
