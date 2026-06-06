from app.core.enums import AccountStatus


OPERATION_ALLOWED_STATUSES = {
    "BUY_ORDER": {AccountStatus.NORMAL.value},
    "SELL_ORDER": {AccountStatus.NORMAL.value},
    "CANCEL_ORDER": {AccountStatus.NORMAL.value, AccountStatus.FROZEN.value},
    "SETTLEMENT": {AccountStatus.NORMAL.value, AccountStatus.FROZEN.value},
    "ACCOUNT_FREEZE": {AccountStatus.NORMAL.value},
    "DEPOSIT": {AccountStatus.NORMAL.value},
    "WITHDRAW": {AccountStatus.NORMAL.value},
    "CHANGE_PWD": {AccountStatus.NORMAL.value},
    "LOST": {AccountStatus.NORMAL.value},
    "REISSUE": {AccountStatus.LOST.value},
    "CANCEL": {AccountStatus.NORMAL.value},
    "QUERY": {
        AccountStatus.NORMAL.value,
        AccountStatus.FROZEN.value,
        AccountStatus.LOST.value,
    },
}


def allowed_statuses(operation_type: str) -> set[str] | None:
    return OPERATION_ALLOWED_STATUSES.get(operation_type.upper())


def status_rejection_reason(account_name: str, account_status: str) -> str:
    reasons = {
        AccountStatus.FROZEN.value: f"{account_name}已冻结，不能执行当前业务",
        AccountStatus.LOST.value: f"{account_name}已挂失，不能执行当前业务",
        AccountStatus.CLOSED.value: f"{account_name}已注销，不能执行当前业务",
    }
    return reasons.get(account_status, f"{account_name}状态异常({account_status})")
