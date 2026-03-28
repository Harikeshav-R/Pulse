"""Background task scheduler for periodic trial oversight activities."""

import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.models.checkin import CheckinSession

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def check_missed_checkins() -> None:
    """Find checkins scheduled >24h ago that are not completed, mark abandoned, and notify bus."""
    # Import inside to avoid circular deps during startup
    from app.main import async_session_factory, event_bus

    if not async_session_factory or not event_bus:
        logger.warning("Scheduler: async_session_factory or event_bus not initialized")
        return

    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    async with async_session_factory() as db:
        result = await db.execute(
            select(CheckinSession).where(
                CheckinSession.status.in_(["scheduled", "in_progress"]),
                CheckinSession.started_at <= cutoff,
            )
        )
        late_sessions = result.scalars().all()

        for session in late_sessions:
            session.status = "abandoned"
            logger.info("Marking session %s as abandoned (missed checkin)", session.id)

            recent_sessions = (
                await db.execute(
                    select(CheckinSession)
                    .where(CheckinSession.patient_id == session.patient_id)
                    .order_by(CheckinSession.started_at.desc())
                )
            ).scalars().all()

            consecutive_misses = 0
            for rs in recent_sessions:
                # the current session object hasn't been committed, but we updated rs.status in the DB if rs refers to the same object or not
                if rs.id == session.id or rs.status in ["abandoned", "missed"]:
                    consecutive_misses += 1
                elif rs.status == "completed":
                    break

            await event_bus.publish(
                "checkin.missed",
                {
                    "patient_id": str(session.patient_id),
                    "session_id": str(session.id),
                    "consecutive_misses": consecutive_misses,
                },
            )

        await db.commit()


def start_scheduler() -> None:
    """Start the APScheduler background tasks."""
    scheduler.add_job(
        check_missed_checkins,
        "interval",
        hours=1,
        id="check_missed_checkins",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started with job: check_missed_checkins (1h interval)")


def stop_scheduler() -> None:
    """Stop the APScheduler background tasks."""
    scheduler.shutdown(wait=False)
