from datetime import datetime

from app.core.enums import AccountStatus
from app.schemas.common import OrmModel


class SecuritiesAccountResponse(OrmModel):
    security_account_id: str
    investor_id: str
    account_status: AccountStatus
    created_at: datetime
    updated_at: datetime
