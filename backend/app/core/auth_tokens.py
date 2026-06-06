import base64
import binascii
import hashlib
import hmac
import json
import time
from typing import Any

from fastapi import HTTPException, status

from app.core.config import settings


def _encode_part(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _decode_part(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    decoded = base64.urlsafe_b64decode(data + padding)
    if _encode_part(decoded) != data:
        raise ValueError
    return decoded


def issue_access_token(
    *,
    investor_id: str,
    fund_account_id: str,
    security_account_id: str,
    expires_at: int,
) -> str:
    payload = {
        "token_type": "INVESTOR",
        "investor_id": investor_id,
        "fund_account_id": fund_account_id,
        "security_account_id": security_account_id,
        "exp": expires_at,
    }
    encoded_payload = _encode_part(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    signature = hmac.new(
        settings.auth_token_secret.encode("utf-8"),
        encoded_payload.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{encoded_payload}.{_encode_part(signature)}"


def verify_access_token(token: str) -> dict[str, Any]:
    try:
        encoded_payload, encoded_signature = token.split(".", 1)
        expected_signature = hmac.new(
            settings.auth_token_secret.encode("utf-8"),
            encoded_payload.encode("ascii"),
            hashlib.sha256,
        ).digest()
        supplied_signature = _decode_part(encoded_signature)
        if not hmac.compare_digest(expected_signature, supplied_signature):
            raise ValueError
        payload = json.loads(_decode_part(encoded_payload))
        if payload.get("token_type") != "INVESTOR":
            raise ValueError
        if int(payload["exp"]) <= int(time.time()):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="访问令牌已过期",
            )
        for field in ("investor_id", "fund_account_id", "security_account_id"):
            if not isinstance(payload.get(field), str) or not payload[field]:
                raise ValueError
        return payload
    except HTTPException:
        raise
    except (
        binascii.Error,
        KeyError,
        TypeError,
        UnicodeDecodeError,
        ValueError,
        json.JSONDecodeError,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="访问令牌无效",
        )
