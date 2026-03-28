"""Analytics service — aggregate queries for trial oversight dashboards."""

import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import RiskScore
from app.models.checkin import CheckinSession
from app.models.patient import Patient
from app.models.symptom import SymptomEntry
from app.models.trial import Site

logger = logging.getLogger(__name__)


async def get_symptom_trends(
    trial_id: str,
    days: int,
    db: AsyncSession,
) -> list[dict]:
    """Get daily symptom counts grouped by MedDRA term."""
    tid = uuid.UUID(trial_id)
    since = datetime.now(timezone.utc) - timedelta(days=days)

    sites = (await db.execute(
        select(Site.id).where(Site.trial_id == tid)
    )).scalars().all()
    patients = (await db.execute(
        select(Patient.id).where(Patient.site_id.in_(sites))
    )).scalars().all()

    result = await db.execute(
        select(
            func.date_trunc("day", SymptomEntry.created_at).label("day"),
            SymptomEntry.meddra_pt_term,
            func.count(SymptomEntry.id).label("count"),
        )
        .where(
            SymptomEntry.patient_id.in_(patients),
            SymptomEntry.created_at >= since,
        )
        .group_by("day", SymptomEntry.meddra_pt_term)
        .order_by("day")
    )

    return [
        {
            "date": row.day.isoformat() if row.day else None,
            "term": row.meddra_pt_term,
            "count": row.count,
        }
        for row in result.all()
    ]


async def get_risk_score_history(
    patient_id: str,
    days: int,
    db: AsyncSession,
) -> list[dict]:
    """Get risk score history for a patient."""
    pid = uuid.UUID(patient_id)
    since = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(RiskScore)
        .where(RiskScore.patient_id == pid, RiskScore.calculated_at >= since)
        .order_by(RiskScore.calculated_at)
    )

    return [
        {
            "score": r.score,
            "tier": r.tier,
            "symptom": r.symptom_component,
            "wearable": r.wearable_component,
            "engagement": r.engagement_component,
            "compliance": r.compliance_component,
            "calculated_at": r.calculated_at.isoformat() if r.calculated_at else None,
        }
        for r in result.scalars().all()
    ]


async def get_checkin_compliance(
    trial_id: str,
    days: int,
    db: AsyncSession,
) -> dict:
    """Get check-in compliance statistics across the trial."""
    tid = uuid.UUID(trial_id)
    since = datetime.now(timezone.utc) - timedelta(days=days)

    sites = (await db.execute(
        select(Site.id).where(Site.trial_id == tid)
    )).scalars().all()
    patients = (await db.execute(
        select(Patient).where(Patient.site_id.in_(sites))
    )).scalars().all()
    patient_ids = [p.id for p in patients]

    total = (await db.execute(
        select(func.count(CheckinSession.id))
        .where(
            CheckinSession.patient_id.in_(patient_ids),
            CheckinSession.started_at >= since,
        )
    )).scalar() or 0

    completed = (await db.execute(
        select(func.count(CheckinSession.id))
        .where(
            CheckinSession.patient_id.in_(patient_ids),
            CheckinSession.started_at >= since,
            CheckinSession.status == "completed",
        )
    )).scalar() or 0

    abandoned = (await db.execute(
        select(func.count(CheckinSession.id))
        .where(
            CheckinSession.patient_id.in_(patient_ids),
            CheckinSession.started_at >= since,
            CheckinSession.status == "abandoned",
        )
    )).scalar() or 0

    return {
        "trial_id": trial_id,
        "period_days": days,
        "total_sessions": total,
        "completed": completed,
        "abandoned": abandoned,
        "compliance_rate": round(completed / max(total, 1), 3),
        "total_patients": len(patients),
    }
