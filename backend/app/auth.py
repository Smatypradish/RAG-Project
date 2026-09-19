"""Minimal, dependency-free bearer token authentication.

Tokens are HMAC-SHA256 signed with the admin password as the secret and carry
an expiry timestamp. No third-party JWT library is required.
"""
import base64
import hashlib
import hmac
import json
import time
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings

bearer_scheme = HTTPBearer(auto_error=False)


def _sign(payload_b64: str, secret: str) -> str:
    return base64.urlsafe_b64encode(
        hmac.new(secret.encode(), payload_b64.encode(), hashlib.sha256).digest()
    ).decode().rstrip("=")


def issue_token(username: str) -> str:
    settings = get_settings()
    expires_at = int(time.time()) + settings.session_ttl_minutes * 60
    payload = {"sub": username, "exp": expires_at}
    payload_b64 = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode()
    ).decode().rstrip("=")
    return f"{payload_b64}.{_sign(payload_b64, settings.admin_password)}"


def verify_token(token: str) -> Optional[str]:
    settings = get_settings()
    if not settings.admin_password:
        return None
    try:
        payload_b64, signature = token.split(".", 1)
    except ValueError:
        return None
    expected = _sign(payload_b64, settings.admin_password)
    if not hmac.compare_digest(signature, expected):
        return None
    try:
        padded = payload_b64 + "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded.encode()))
    except (ValueError, json.JSONDecodeError):
        return None
    if payload.get("sub") != settings.admin_username:
        return None
    if int(payload.get("exp", 0)) < int(time.time()):
        return None
    return payload["sub"]


def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    subject = verify_token(credentials.credentials)
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )
    return subject
