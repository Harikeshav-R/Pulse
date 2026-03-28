"""Dashboard service — aggregated views for the researcher web dashboard."""

import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert, RiskScore
from app.models.checkin import CheckinSession
from app.models.patient import Patient
from app.models.symptom import SymptomEntry
from app.models.trial import Site

logger = logging.getLogger(__name__)


async def get_trial_overview(trial_id: str, db: AsyncSession) -> dict:
    """Get high-level trial overview with patient counts and alert summary."""
    logger.info("Loading trial overview: trial_id=%s", trial_id)
    tid = uuid.UUID(trial_id)

    # Get all sites and patients for this trial
    sites = (await db.execute(
        select(Site).where(Site.trial_id == tid)
    )).scalars().all()
    site_ids = [s.id for s in sites]

    patients = (await db.execute(
        select(Patient).where(Patient.site_id.in_(site_ids))
    )).scalars().all()
    patient_ids = [p.id for p in patients]

    # Open alerts by severity
    alert_counts = {}
    for severity in ("critical", "high", "medium", "low"):
        count = (await db.execute(
            select(func.count(Alert.id))
            .where(
                Alert.patient_id.in_(patient_ids),
                Alert.status.in_(["open", "acknowledged"]),
                Alert.severity == severity,
            )
        )).scalar() or 0
        alert_counts[severity] = count

    # Risk score distribution
    risk_dist = {"low": 0, "medium": 0, "high": 0}
    for pid in patient_ids:
        latest = (await db.execute(
            select(RiskScore)
            .where(RiskScore.patient_id == pid)
            .order_by(RiskScore.calculated_at.desc())
            .limit(1)
        )).scalars().first()
        if latest:
            risk_dist[latest.tier] = risk_dist.get(latest.tier, 0) + 1
        else:
            risk_dist["low"] += 1

    # Checkin compliance (last 7 days)
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    checkins_completed = (await db.execute(
        select(func.count(CheckinSession.id))
        .where(
            CheckinSession.patient_id.in_(patient_ids),
            CheckinSession.status == "completed",
            CheckinSession.completed_at >= seven_days_ago,
        )
    )).scalar() or 0

    return {
        "trial_id": trial_id,
        "total_patients": len(patients),
        "total_sites": len(sites),
        "open_alerts": alert_counts,
        "risk_distribution": risk_dist,
        "checkins_last_7_days": checkins_completed,
    }


async def get_patient_detail(patient_id: str, db: AsyncSession) -> dict:
    """Get detailed view of a single patient for the dashboard."""
    pid = uuid.UUID(patient_id)

    patient = (await db.execute(
        select(Patient).where(Patient.id == pid)
    )).scalars().first()
    if not patient:
        raise ValueError(f"Patient not found: {patient_id}")

    # Latest risk score
    risk = (await db.execute(
        select(RiskScore)
        .where(RiskScore.patient_id == pid)
        .order_by(RiskScore.calculated_at.desc())
        .limit(1)
    )).scalars().first()

    # Recent symptoms
    symptoms = (await db.execute(
        select(SymptomEntry)
        .where(SymptomEntry.patient_id == pid)
        .order_by(SymptomEntry.created_at.desc())
        .limit(10)
    )).scalars().all()

    # Recent alerts
    alerts = (await db.execute(
        select(Alert)
        .where(Alert.patient_id == pid)
        .order_by(Alert.created_at.desc())
        .limit(10)
    )).scalars().all()

    # Recent check-ins
    sessions = (await db.execute(
        select(CheckinSession)
        .where(CheckinSession.patient_id == pid)
        .order_by(CheckinSession.started_at.desc())
        .limit(10)
    )).scalars().all()

    return {
        "patient": {
            "id": str(patient.id),
            "subject_id": patient.subject_id,
            "enrollment_code": patient.enrollment_code,
            "status": patient.status,
            "treatment_arm": patient.treatment_arm,
        },
        "risk_score": {
            "score": risk.score if risk else 0,
            "tier": risk.tier if risk else "low",
            "components": {
                "symptom": risk.symptom_component if risk else 0,
                "wearable": risk.wearable_component if risk else 0,
                "engagement": risk.engagement_component if risk else 0,
                "compliance": risk.compliance_component if risk else 0,
            },
        } if risk else None,
        "recent_symptoms": [
            {
                "id": str(s.id),
                "term": s.meddra_pt_term,
                "grade": s.severity_grade,
                "text": s.symptom_text[:100],
                "crc_reviewed": s.crc_reviewed,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in symptoms
        ],
        "recent_alerts": [
            {
                "id": str(a.id),
                "type": a.alert_type,
                "severity": a.severity,
                "title": a.title,
                "status": a.status,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in alerts
        ],
        "recent_checkins": [
            {
                "id": str(cs.id),
                "type": cs.session_type,
                "modality": cs.modality,
                "status": cs.status,
                "duration": cs.duration_seconds,
                "started_at": cs.started_at.isoformat() if cs.started_at else None,
            }
            for cs in sessions
        ],
    }
