from datetime import UTC, datetime


def utc_now() -> datetime:
    """返回适用于当前无时区数据库字段的 UTC 时间。"""
    return datetime.now(UTC).replace(tzinfo=None)


def to_utc_naive(value: datetime) -> datetime:
    """将 API 输入时间统一转换为数据库使用的无时区 UTC 时间。"""
    if value.tzinfo is None:
        return value
    return value.astimezone(UTC).replace(tzinfo=None)
