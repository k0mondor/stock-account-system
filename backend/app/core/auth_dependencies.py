import hmac
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.auth_tokens import verify_access_token
from app.core.config import settings


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
