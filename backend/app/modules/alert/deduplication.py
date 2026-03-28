"""Alert deduplication per TECHNICAL_DOC §9.2."""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert

logger = logging.getLogger(__name__)


async def should_create_alert(
    db: AsyncSession,
    patient_id: str,
    alert_type: str,
    source_type: str | None = None,
    dedup_window_hours: int = 24,
) -> bool:
    """Check if a new alert should be created or deduplicated.

    Prevents duplicate alerts of the same type for the same patient
    within the deduplication window (default 24 hours).
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=dedup_window_hours)

    conditions = [
        Alert.patient_id == patient_id,
        Alert.alert_type == alert_type,
        Alert.created_at >= cutoff,
        Alert.status.in_(["open", "acknowledged"]),
    ]
    if source_type:
        conditions.append(Alert.source_type == source_type)

    result = await db.execute(select(Alert).where(and_(*conditions)).limit(1))
    existing = result.scalars().first()

    if existing:
        logger.info(
            "Alert deduplicated: type=%s, patient=%s (existing=%s)",
            alert_type, patient_id, existing.id,
        )
        return False

    return True
