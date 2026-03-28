"""Dashboard service — aggregated views for the researcher web dashboard."""

import logging
import uuid
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert, RiskScore
from app.models.checkin import CheckinSession
from app.models.patient import Patient
from app.models.symptom import SymptomEntry
from app.models.trial import Site
from app.models.wearable import WearableConnection, WearableReading, WearableAnomaly
from app.schemas.dashboard import (
    PatientListResponse,
    PatientListItem,
    PatientWearableDataResponse,
    DataPoint,
    BaselineData,
    PatientTimelineResponse,
    PatientTimelineEvent,
)
from app.schemas.symptom import SymptomReviewRequest, SymptomReviewResponse

logger = logging.getLogger(__name__)


async def get_trial_overview(trial_id: str, db: AsyncSession) -> dict:
    """Get high-level trial overview with patient counts and alert summary."""
    logger.info("Loading trial overview: trial_id=%s", trial_id)
    tid = uuid.UUID(trial_id)

    # Get all sites and patients for this trial
    sites = (await db.execute(select(Site).where(Site.trial_id == tid))).scalars().all()
    site_ids = [s.id for s in sites]

    patients = (
        (await db.execute(select(Patient).where(Patient.site_id.in_(site_ids)))).scalars().all()
    )
    patient_ids = [p.id for p in patients]

    # Open alerts by severity
    alert_counts = {}
    for severity in ("critical", "high", "medium", "low"):
        count = (
            await db.execute(
                select(func.count(Alert.id)).where(
                    Alert.patient_id.in_(patient_ids),
                    Alert.status.in_(["open", "acknowledged"]),
                    Alert.severity == severity,
                )
            )
        ).scalar() or 0
        alert_counts[severity] = count

    # Risk score distribution
    risk_dist = {"low": 0, "medium": 0, "high": 0}
    for pid in patient_ids:
        latest = (
            (
                await db.execute(
                    select(RiskScore)
                    .where(RiskScore.patient_id == pid)
                    .order_by(RiskScore.calculated_at.desc())
                    .limit(1)
                )
            )
            .scalars()
            .first()
        )
        if latest:
            risk_dist[latest.tier] = risk_dist.get(latest.tier, 0) + 1
        else:
            risk_dist["low"] += 1

    # Checkin compliance (last 7 days)
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    checkins_completed = (
        await db.execute(
            select(func.count(CheckinSession.id)).where(
                CheckinSession.patient_id.in_(patient_ids),
                CheckinSession.status == "completed",
                CheckinSession.completed_at >= seven_days_ago,
            )
        )
    ).scalar() or 0

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

    patient = (await db.execute(select(Patient).where(Patient.id == pid))).scalars().first()
    if not patient:
        raise ValueError(f"Patient not found: {patient_id}")

    # Latest risk score
    risk = (
        (
            await db.execute(
                select(RiskScore)
                .where(RiskScore.patient_id == pid)
                .order_by(RiskScore.calculated_at.desc())
                .limit(1)
            )
        )
        .scalars()
        .first()
    )

    # Recent symptoms
    symptoms = (
        (
            await db.execute(
                select(SymptomEntry)
                .where(SymptomEntry.patient_id == pid)
                .order_by(SymptomEntry.created_at.desc())
                .limit(10)
            )
        )
        .scalars()
        .all()
    )

    # Recent alerts
    alerts = (
        (
            await db.execute(
                select(Alert)
                .where(Alert.patient_id == pid)
                .order_by(Alert.created_at.desc())
                .limit(10)
            )
        )
        .scalars()
        .all()
    )

    # Recent check-ins
    sessions = (
        (
            await db.execute(
                select(CheckinSession)
                .where(CheckinSession.patient_id == pid)
                .order_by(CheckinSession.started_at.desc())
                .limit(10)
            )
        )
        .scalars()
        .all()
    )

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
        }
        if risk
        else None,
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


async def get_patient_list(
    trial_id: str, limit: int, offset: int, db: AsyncSession
) -> PatientListResponse:
    tid = uuid.UUID(trial_id)
    sites = (await db.execute(select(Site).where(Site.trial_id == tid))).scalars().all()
    if not sites:
        return PatientListResponse(patients=[], total=0, page=offset // limit + 1)

    site_ids = [s.id for s in sites]
    total = (
        await db.execute(select(func.count(Patient.id)).where(Patient.site_id.in_(site_ids)))
    ).scalar() or 0

    patients = (
        (
            await db.execute(
                select(Patient).where(Patient.site_id.in_(site_ids)).offset(offset).limit(limit)
            )
        )
        .scalars()
        .all()
    )

    items = []
    for p in patients:
        risk = (
            (
                await db.execute(
                    select(RiskScore)
                    .where(RiskScore.patient_id == p.id)
                    .order_by(RiskScore.calculated_at.desc())
                    .limit(1)
                )
            )
            .scalars()
            .first()
        )
        acount = (
            await db.execute(
                select(func.count(Alert.id)).where(
                    Alert.patient_id == p.id, Alert.status.in_(["open", "acknowledged"])
                )
            )
        ).scalar() or 0
        last_c = (
            (
                await db.execute(
                    select(CheckinSession.started_at)
                    .where(CheckinSession.patient_id == p.id)
                    .order_by(CheckinSession.started_at.desc())
                    .limit(1)
                )
            )
            .scalars()
            .first()
        )
        warn_active = (
            await db.execute(
                select(WearableConnection).where(
                    WearableConnection.patient_id == p.id, WearableConnection.is_active.is_(True)
                )
            )
        ).scalars().first() is not None

        symptom = (
            (
                await db.execute(
                    select(SymptomEntry)
                    .where(SymptomEntry.patient_id == p.id)
                    .order_by(SymptomEntry.created_at.desc())
                    .limit(1)
                )
            )
            .scalars()
            .first()
        )
        latest_sym = None
        if symptom:
            term = symptom.meddra_pt_term or symptom.symptom_text
            latest_sym = (
                f"{term} (Grade {symptom.severity_grade})" if symptom.severity_grade else term
            )

        items.append(
            PatientListItem(
                patient_id=str(p.id),
                subject_id=p.subject_id,
                treatment_arm=p.treatment_arm,
                risk_score=risk.score if risk else 0,
                risk_tier=risk.tier if risk else "low",
                last_checkin_at=last_c,
                open_alerts=acount,
                latest_symptom=latest_sym,
                wearable_status=warn_active,
            )
        )

    return PatientListResponse(patients=items, total=total, page=(offset // limit) + 1)


async def get_patient_symptoms(
    patient_id: str, status: str | None, db: AsyncSession
) -> list[dict]:
    pid = uuid.UUID(patient_id)
    query = select(SymptomEntry).where(SymptomEntry.patient_id == pid)

    if status == "pending_review":
        query = query.where(SymptomEntry.crc_reviewed.is_(False))

    query = query.order_by(SymptomEntry.created_at.desc())
    symptoms = (await db.execute(query)).scalars().all()

    return [
        {
            "id": str(s.id),
            "symptom_text": s.symptom_text,
            "meddra_pt_term": s.meddra_pt_term,
            "severity_grade": s.severity_grade,
            "onset_date": s.onset_date,
            "is_ongoing": s.is_ongoing,
            "created_at": s.created_at,
            "ai_confidence": s.ai_confidence,
            "crc_reviewed": s.crc_reviewed,
            "crc_reviewed_by": str(s.crc_reviewed_by) if s.crc_reviewed_by else None,
            "crc_reviewed_at": s.crc_reviewed_at,
        }
        for s in symptoms
    ]


async def review_symptom(
    symptom_id: str, request: SymptomReviewRequest, staff_id: str, db: AsyncSession
) -> SymptomReviewResponse:
    sid = uuid.UUID(symptom_id)
    symptom = await db.get(SymptomEntry, sid)
    if not symptom:
        raise ValueError("Symptom not found")

    if request.action == "override":
        if request.override_term:
            symptom.meddra_pt_term = request.override_term
            symptom.crc_override_term = request.override_term
        if request.override_grade is not None:
            symptom.severity_grade = request.override_grade
            symptom.crc_override_grade = request.override_grade

    symptom.crc_reviewed = True
    symptom.crc_reviewed_by = uuid.UUID(staff_id)
    symptom.crc_reviewed_at = datetime.now(timezone.utc)

    await db.commit()

    return SymptomReviewResponse(
        symptom_id=symptom_id,
        crc_reviewed=True,
        reviewed_at=symptom.crc_reviewed_at,
        reviewed_by=staff_id,
    )


async def get_patient_wearable_summary(
    patient_id: str, metric: str, days: int, db: AsyncSession
) -> PatientWearableDataResponse:
    pid = uuid.UUID(patient_id)
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    day_trunc = func.date_trunc("day", WearableReading.recorded_at)
    avg_val = func.avg(WearableReading.value)

    query = (
        select(day_trunc.label("day"), avg_val.label("avg_val"))
        .where(
            WearableReading.patient_id == pid,
            WearableReading.metric == metric,
            WearableReading.recorded_at >= cutoff,
        )
        .group_by(day_trunc)
        .order_by(day_trunc)
    )
    result = await db.execute(query)

    points = []
    vals = []
    for row in result:
        day_val, avg_v = row.day, row.avg_val
        if day_val is not None and avg_v is not None:
            if isinstance(day_val, str):
                dt_val = datetime.fromisoformat(day_val)
            elif isinstance(day_val, date) and not isinstance(day_val, datetime):
                dt_val = datetime(day_val.year, day_val.month, day_val.day, tzinfo=timezone.utc)
            else:
                dt_val = day_val
            if dt_val.tzinfo is None:
                dt_val = dt_val.replace(tzinfo=timezone.utc)
            points.append(DataPoint(timestamp=dt_val, value=float(avg_v)))
            vals.append(float(avg_v))

    baseline = None
    if len(vals) > 0:
        mean = sum(vals) / len(vals)
        variance = sum((x - mean) ** 2 for x in vals) / len(vals)
        stddev = variance**0.5
        baseline = BaselineData(mean=mean, stddev=stddev)

    return PatientWearableDataResponse(data_points=points, baseline=baseline, anomalies=[])


async def get_patient_timeline(patient_id: str, db: AsyncSession) -> PatientTimelineResponse:
    pid = uuid.UUID(patient_id)
    events = []

    checkins = (
        (
            await db.execute(
                select(CheckinSession).where(
                    CheckinSession.patient_id == pid, CheckinSession.status == "completed"
                )
            )
        )
        .scalars()
        .all()
    )
    for c in checkins:
        if c.completed_at:
            events.append(
                PatientTimelineEvent(
                    type="checkin",
                    timestamp=c.completed_at,
                    title="Check-in Completed",
                    details=f"Modality: {c.modality}, Duration: {c.duration_seconds}s",
                    severity="info",
                )
            )

    symptoms = (
        (await db.execute(select(SymptomEntry).where(SymptomEntry.patient_id == pid)))
        .scalars()
        .all()
    )
    for s in symptoms:
        term = s.meddra_pt_term or s.symptom_text
        events.append(
            PatientTimelineEvent(
                type="symptom",
                timestamp=s.created_at,
                title=f"Symptom Reported: {term}",
                details=f"Severity Grade: {s.severity_grade}"
                if s.severity_grade
                else "Unclassified",
                severity="warning" if s.severity_grade and s.severity_grade >= 2 else "info",
            )
        )

    anomalies = (
        (await db.execute(select(WearableAnomaly).where(WearableAnomaly.patient_id == pid)))
        .scalars()
        .all()
    )
    for a in anomalies:
        events.append(
            PatientTimelineEvent(
                type="wearable_anomaly",
                timestamp=a.detected_at,
                title=f"Anomaly: {a.metric} ({a.anomaly_type})",
                details=f"Value: {a.value:.1f}, Severity: {a.severity}",
                severity=a.severity,
            )
        )

    alerts = (await db.execute(select(Alert).where(Alert.patient_id == pid))).scalars().all()
    for a in alerts:
        events.append(
            PatientTimelineEvent(
                type="alert",
                timestamp=a.created_at,
                title=f"Alert: {a.title}",
                details=a.description,
                severity=a.severity,
            )
        )

    events.sort(key=lambda x: x.timestamp, reverse=True)
    return PatientTimelineResponse(events=events)
