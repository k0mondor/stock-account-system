import hmac
from typing import Any

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.auth_tokens import verify_access_token
from app.core.config import settings
from app.core.enums import StaffRole, StaffStatus
from app.db.session import get_db
from app.models.base_data import Staff


bearer_scheme = HTTPBearer(auto_error=False)


def require_access_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少 Bearer 访问令牌",
        )
    token = credentials.credentials
    if settings.service_token and hmac.compare_digest(token, settings.service_token):
        return {"token_type": "SERVICE"}
    return verify_access_token(token)


def require_service_token(
    claims: dict[str, Any] = Depends(require_access_token),
) -> dict[str, Any]:
    if claims["token_type"] != "SERVICE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="该接口仅允许内部服务调用",
        )
    return claims


def authorize_fund_account(
    fund_account_id: str,
    claims: dict[str, Any] = Depends(require_access_token),
) -> dict[str, Any]:
    if (
        claims["token_type"] != "SERVICE"
        and claims["fund_account_id"] != fund_account_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="访问令牌与资金账户不匹配",
        )
    return claims


def authorize_security_account(
    security_account_id: str,
    claims: dict[str, Any] = Depends(require_access_token),
) -> dict[str, Any]:
    if (
        claims["token_type"] != "SERVICE"
        and claims["security_account_id"] != security_account_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="访问令牌与证券账户不匹配",
        )
    return claims


def require_staff_actor(*allowed_roles: StaffRole | str):
    normalized_roles = {
        role.value if isinstance(role, StaffRole) else str(role)
        for role in allowed_roles
    }

    def dependency(
        staff_id: str | None = Header(None, alias="X-Staff-Id"),
        claims: dict[str, Any] = Depends(require_service_token),
        db: Session = Depends(get_db),
    ) -> Staff:
        del claims
        if not staff_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="缺少当前工作人员身份信息",
            )
        staff = db.get(Staff, staff_id)
        if not staff:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="当前工作人员不存在",
            )
        if staff.staff_status != StaffStatus.ACTIVE.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="当前工作人员状态不可用",
            )
        if normalized_roles and staff.role not in normalized_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="当前工作人员无权限执行该操作",
            )
        return staff

    return dependency
