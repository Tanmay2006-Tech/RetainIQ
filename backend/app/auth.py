from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
import secrets
from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


@dataclass(frozen=True)
class AuthSettings:
    username: str
    password: str
    secret_key: str
    algorithm: str
    access_token_ttl_minutes: int


def get_auth_settings() -> AuthSettings:
    username = os.getenv("CHURN_ADMIN_USER", "admin")
    password = os.getenv("CHURN_ADMIN_PASSWORD", "churn123")
    secret_key = os.getenv("CHURN_JWT_SECRET", "change-me-in-production-please-32chars")
    algorithm = os.getenv("CHURN_JWT_ALGORITHM", "HS256")
    access_token_ttl_minutes = int(os.getenv("CHURN_JWT_TTL_MINUTES", "480"))
    return AuthSettings(
        username=username,
        password=password,
        secret_key=secret_key,
        algorithm=algorithm,
        access_token_ttl_minutes=access_token_ttl_minutes,
    )


def verify_credentials(username: str, password: str) -> bool:
    cfg = get_auth_settings()
    return secrets.compare_digest(username, cfg.username) and secrets.compare_digest(
        password, cfg.password
    )


def create_access_token(username: str) -> str:
    cfg = get_auth_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=cfg.access_token_ttl_minutes)).timestamp()),
    }
    return jwt.encode(payload, cfg.secret_key, algorithm=cfg.algorithm)


bearer_scheme = HTTPBearer(auto_error=False)


def require_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )

    token = credentials.credentials
    cfg = get_auth_settings()
    try:
        decoded = jwt.decode(token, cfg.secret_key, algorithms=[cfg.algorithm])
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc

    subject = decoded.get("sub")
    if not isinstance(subject, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    return subject
