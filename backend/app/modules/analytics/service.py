"""Analytics service — aggregate queries for trial oversight dashboards."""

import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import RiskScore
from app.models.checkin import CheckinSession
from app.models.patient import Patient
from app.models.symptom import SymptomEntry
from app.models.trial import Site
from app.models.wearable import WearableReading
from sqlalchemy import cast, Float

logger = logging.getLogger(__name__)


async def get_symptom_trends(
    trial_id: str,
    days: int,
    db: AsyncSession,
) -> list[dict]:
    """Get daily symptom counts grouped by MedDRA term."""
    tid = uuid.UUID(trial_id)
    since = datetime.now(timezone.utc) - timedelta(days=days)

    sites = (await db.execute(select(Site.id).where(Site.trial_id == tid))).scalars().all()
    patients = (
        (await db.execute(select(Patient.id).where(Patient.site_id.in_(sites)))).scalars().all()
    )

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

    sites = (await db.execute(select(Site.id).where(Site.trial_id == tid))).scalars().all()
    patients = (await db.execute(select(Patient).where(Patient.site_id.in_(sites)))).scalars().all()
    patient_ids = [p.id for p in patients]

    total = (
        await db.execute(
            select(func.count(CheckinSession.id)).where(
                CheckinSession.patient_id.in_(patient_ids),
                CheckinSession.started_at >= since,
            )
        )
    ).scalar() or 0

    completed = (
        await db.execute(
            select(func.count(CheckinSession.id)).where(
                CheckinSession.patient_id.in_(patient_ids),
                CheckinSession.started_at >= since,
                CheckinSession.status == "completed",
            )
        )
    ).scalar() or 0

    abandoned = (
        await db.execute(
            select(func.count(CheckinSession.id)).where(
                CheckinSession.patient_id.in_(patient_ids),
                CheckinSession.started_at >= since,
                CheckinSession.status == "abandoned",
            )
        )
    ).scalar() or 0

    return {
        "trial_id": trial_id,
        "period_days": days,
        "total_sessions": total,
        "completed": completed,
        "abandoned": abandoned,
        "compliance_rate": round(completed / max(total, 1), 3),
        "total_patients": len(patients),
    }


async def get_adverse_events_incidence(trial_id: str, days: int, db: AsyncSession) -> list[dict]:
    tid = uuid.UUID(trial_id)
    since = datetime.now(timezone.utc) - timedelta(days=days)

    sites = (await db.execute(select(Site.id).where(Site.trial_id == tid))).scalars().all()

    query = (
        select(
            Patient.treatment_arm,
            SymptomEntry.meddra_pt_term,
            func.count(SymptomEntry.id).label("occurrence_count"),
            func.count(func.distinct(SymptomEntry.patient_id)).label("unique_patients"),
        )
        .join(Patient, SymptomEntry.patient_id == Patient.id)
        .where(Patient.site_id.in_(sites), SymptomEntry.created_at >= since)
        .group_by(Patient.treatment_arm, SymptomEntry.meddra_pt_term)
        .order_by(Patient.treatment_arm, func.count(SymptomEntry.id).desc())
    )
    result = await db.execute(query)

    return [
        {
            "treatment_arm": row.treatment_arm or "Unassigned",
            "term": row.meddra_pt_term or "Unclassified",
            "occurrence_count": row.occurrence_count,
            "unique_patients": row.unique_patients,
        }
        for row in result.all()
    ]


async def get_wearable_distributions(
    trial_id: str, metric: str, days: int, db: AsyncSession
) -> list[dict]:
    tid = uuid.UUID(trial_id)
    since = datetime.now(timezone.utc) - timedelta(days=days)
    sites = (await db.execute(select(Site.id).where(Site.trial_id == tid))).scalars().all()

    query = (
        select(
            Patient.treatment_arm,
            func.avg(cast(WearableReading.value, Float)).label("avg_val"),
            func.min(cast(WearableReading.value, Float)).label("min_val"),
            func.max(cast(WearableReading.value, Float)).label("max_val"),
        )
        .join(Patient, WearableReading.patient_id == Patient.id)
        .where(
            Patient.site_id.in_(sites),
            WearableReading.metric == metric,
            WearableReading.recorded_at >= since,
        )
        .group_by(Patient.treatment_arm)
    )

    result = await db.execute(query)
    return [
        {
            "treatment_arm": row.treatment_arm or "Unassigned",
            "average": float(row.avg_val) if row.avg_val is not None else None,
            "min": float(row.min_val) if row.min_val is not None else None,
            "max": float(row.max_val) if row.max_val is not None else None,
        }
        for row in result.all()
    ]
