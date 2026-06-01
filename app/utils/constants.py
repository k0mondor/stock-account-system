"""系统常量定义"""

from enum import Enum


class PasswordType(str, Enum):
    """密码类型"""
    TRADE = "TRADE"  # 交易密码
    WITHDRAW = "WITHDRAW"  # 取款密码


class AccountStatus(str, Enum):
    """账户状态"""
    NORMAL = "NORMAL"  # 正常
    FROZEN = "FROZEN"  # 冻结
    LOST = "LOST"  # 挂失
    CLOSED = "CLOSED"  # 关闭


class AccountType(str, Enum):
    """账户类型"""
    FUND = "FUND"  # 资金账户
    SECURITY = "SECURITY"  # 证券账户


class AssociationStatus(str, Enum):
    """账户关联状态"""
    ACTIVE = "ACTIVE"  # 有效绑定
    UNLINKED = "UNLINKED"  # 未绑定


class FundChangeType(str, Enum):
    """资金变更类型"""
    FREEZE = "FREEZE"  # 冻结
    RELEASE = "RELEASE"  # 释放
    DEDUCT = "DEDUCT"  # 扣款
    INCREASE = "INCREASE"  # 增加


class PositionChangeType(str, Enum):
    """持仓变更类型"""
    FREEZE = "FREEZE"  # 冻结
    RELEASE = "RELEASE"  # 释放
    DEDUCT = "DEDUCT"  # 扣除
    INCREASE = "INCREASE"  # 增加


# 错误码
ERROR_CODES = {
    "COMMON_BAD_REQUEST": 40001,
    "COMMON_UNAUTHORIZED": 40101,
    "COMMON_FORBIDDEN": 40301,
    "COMMON_NOT_FOUND": 40401,
    "COMMON_CONFLICT": 40901,
    "COMMON_INTERNAL_ERROR": 50001,
    "TRADE_E01": 50101,  # 字段缺失
    "TRADE_E02": 50102,  # 股票不存在
    "TRADE_E03": 50103,  # 股票不可交易
    "TRADE_E04": 50104,  # 买卖方向无效
    "TRADE_E05": 50105,  # 价格非法或超出涨跌停
    "TRADE_E06": 50106,  # 数量非法
    "TRADE_E07": 50107,  # 状态不允许撤销
    "ACCOUNT_INSUFFICIENT_FUNDS": 50201,  # 可用资金不足
    "ACCOUNT_INSUFFICIENT_POSITION": 50202,  # 可用持仓不足
    "ACCOUNT_STATUS_BLOCKED": 50203,  # 账户状态不允许
    "INFO_VIP_REQUIRED": 50301,  # 需要VIP权限
    "ADMIN_STOCK_SCOPE_DENIED": 50401,  # 无目标股票权限
}
