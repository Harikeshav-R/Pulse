"""JWT token creation and verification."""

import logging
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.config import settings

logger = logging.getLogger(__name__)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token with the given claims."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(hours=settings.JWT_EXPIRY_HOURS)
    )
    to_encode["exp"] = expire
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    logger.info(
        "JWT created for role=%s, expires=%s",
        data.get("role", "unknown"),
        expire.isoformat(),
    )
    return token


def decode_access_token(token: str) -> dict:
    """Decode a JWT and return the claims payload."""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
