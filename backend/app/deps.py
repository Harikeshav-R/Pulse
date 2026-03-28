"""Dependency injection providers for FastAPI endpoints.

All database sessions, Redis clients, event bus access, and auth extraction
are provided via FastAPI's Depends() system per AGENTS.md §4.1.
"""

import logging
from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


# ─── Database Session ───


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session, auto-closing on exit."""
    from app.main import async_session_factory

    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ─── Redis Client ───


async def get_redis():
    """Return the global Redis client."""
    from app.main import redis_client

    return redis_client


# ─── Event Bus ───


async def get_event_bus():
    """Return the global EventBus instance."""
    from app.main import event_bus

    return event_bus


# ─── WebSocket Manager ───


async def get_ws_manager():
    """Return the global WebSocketManager instance."""
    from app.main import ws_manager

    return ws_manager


# ─── Authentication ───


def _decode_token(token: str) -> dict:
    """Decode and validate a JWT, returning the claims payload."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as exc:
        logger.warning("JWT decode failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


async def get_current_patient(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    """Extract and validate patient claims from JWT Bearer token."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    payload = _decode_token(credentials.credentials)
    if payload.get("role") != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patient access required",
        )
    logger.debug("Authenticated patient: %s", payload.get("patient_id"))
    return payload


async def get_current_staff(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    """Extract and validate staff claims from JWT Bearer token."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    payload = _decode_token(credentials.credentials)
    if payload.get("role") not in ("crc", "pi", "medical_monitor", "study_manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff access required",
        )
    logger.debug("Authenticated staff: %s (role=%s)", payload.get("staff_id"), payload.get("role"))
    return payload
