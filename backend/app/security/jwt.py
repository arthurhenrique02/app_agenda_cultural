"""JWT token utilities for Agenda Cultural."""

from datetime import UTC, datetime, timedelta

import jwt

from app.config import settings

ALGORITHM = "HS256"


def create_access_token(subject: str) -> str:
    """Create a JWT access token valid for ACCESS_TOKEN_EXPIRE_MINUTES minutes."""
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": subject,
        "exp": expire,
        "token_type": "access",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """Create a JWT refresh token valid for REFRESH_TOKEN_EXPIRE_DAYS days."""
    expire = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": subject,
        "exp": expire,
        "token_type": "refresh",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)
