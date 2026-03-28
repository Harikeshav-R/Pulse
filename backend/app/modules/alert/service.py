"""Alert engine service — event handlers for creating and managing alerts."""

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert, RiskScore
from app.models.patient import Patient
from app.models.trial import Site
from app.modules.alert.deduplication import should_create_alert
from app.modules.alert.risk_scoring import calculate_risk_score

logger = logging.getLogger(__name__)


async def handle_symptom_reported(payload: dict) -> None:
    """Event handler for symptom.reported — evaluate alert rules and create alerts."""
    from app.main import async_session_factory, event_bus, ws_manager

    patient_id = payload["patient_id"]
    severity = payload.get("severity_grade", 0)
    symptom_term = payload.get("meddra_pt_term", "Unknown symptom")
    confidence = payload.get("ai_confidence", 0)

    logger.info(
        "Alert engine: evaluating symptom: patient=%s, term=%s, grade=%d",
        patient_id, symptom_term, severity,
    )

    async with async_session_factory() as db:
        # Rule: Grade 3+ symptoms trigger alerts
        if severity >= 3:
            if await should_create_alert(db, patient_id, "symptom_severe"):
                severity_level = "critical" if severity >= 4 else "high"
                alert = Alert(
                    patient_id=uuid.UUID(patient_id),
                    alert_type="symptom_severe",
                    severity=severity_level,
                    title=f"Grade {severity} {symptom_term} reported",
                    description=(
                        f"Patient reported {symptom_term} (Grade {severity}) "
                        f"during check-in. AI confidence: {confidence:.0%}."
                    ),
                    source_type="symptom_entry",
                    source_id=uuid.UUID(payload.get("symptom_entry_id", str(uuid.uuid4()))),
                )
                db.add(alert)
                await db.flush()
                logger.info("Alert created: %s (severity=%s)", alert.title, severity_level)

                # Broadcast to dashboard
                trial_id = await _get_trial_id(patient_id, db)
                if trial_id and ws_manager:
                    await ws_manager.broadcast(trial_id, "alert.created", {
                        "alert_id": str(alert.id),
                        "patient_id": patient_id,
                        "severity": severity_level,
                        "title": alert.title,
                    })

        # Recalculate risk score
        risk = await calculate_risk_score(patient_id, db)

        # Check for risk tier escalation
        prev_risk = await db.execute(
            select(RiskScore)
            .where(RiskScore.patient_id == uuid.UUID(patient_id))
            .order_by(RiskScore.calculated_at.desc())
            .offset(1)
            .limit(1)
        )
        prev = prev_risk.scalars().first()
        if prev and risk["tier"] == "high" and prev.tier != "high":
            if await should_create_alert(db, patient_id, "risk_score_elevated"):
                alert = Alert(
                    patient_id=uuid.UUID(patient_id),
                    alert_type="risk_score_elevated",
                    severity="high",
                    title=f"Patient risk score elevated to HIGH",
                    description=(
                        f"Risk score increased from {prev.score} to {risk['score']}. "
                        f"Contributing factors: {', '.join(risk['factors'])}."
                    ),
                    source_type="system",
                )
                db.add(alert)
                logger.info("Risk escalation alert created for patient %s", patient_id)

        # Broadcast risk score update
        trial_id = await _get_trial_id(patient_id, db)
        if trial_id and ws_manager:
            await ws_manager.broadcast(trial_id, "risk_score.updated", {
                "patient_id": patient_id,
                "score": risk["score"],
                "tier": risk["tier"],
            })

        await db.commit()


async def handle_anomaly_detected(payload: dict) -> None:
    """Event handler for anomaly.detected — create wearable anomaly alerts."""
    from app.main import async_session_factory, ws_manager

    patient_id = payload["patient_id"]
    metric = payload.get("metric", "unknown")
    anomaly_type = payload.get("anomaly_type", "unknown")
    severity = payload.get("severity", "medium")

    logger.info(
        "Alert engine: evaluating anomaly: patient=%s, metric=%s, type=%s",
        patient_id, metric, anomaly_type,
    )

    async with async_session_factory() as db:
        if await should_create_alert(db, patient_id, "wearable_anomaly"):
            alert = Alert(
                patient_id=uuid.UUID(patient_id),
                alert_type="wearable_anomaly",
                severity=severity,
                title=f"{metric.replace('_', ' ').title()} {anomaly_type.replace('_', ' ')} detected",
                description=(
                    f"{metric}: current value {payload.get('value', 'N/A')}, "
                    f"baseline {payload.get('baseline_mean', 'N/A')}. "
                    f"Z-score: {payload.get('z_score', 'N/A')}."
                ),
                source_type="wearable_anomaly",
                source_id=uuid.UUID(payload.get("anomaly_id", str(uuid.uuid4()))),
            )
            db.add(alert)
            await db.flush()

            trial_id = await _get_trial_id(patient_id, db)
            if trial_id and ws_manager:
                await ws_manager.broadcast(trial_id, "alert.created", {
                    "alert_id": str(alert.id),
                    "patient_id": patient_id,
                    "severity": severity,
                    "title": alert.title,
                })

        # Recalculate risk score
        await calculate_risk_score(patient_id, db)
        await db.commit()


async def update_alert(
    alert_id: str,
    action: str,
    note: str | None,
    staff_id: str,
    db: AsyncSession,
) -> dict:
    """Update an alert's status (acknowledge, resolve, dismiss, escalate)."""
    alert = (await db.execute(
        select(Alert).where(Alert.id == uuid.UUID(alert_id))
    )).scalars().first()
    if not alert:
        raise ValueError(f"Alert not found: {alert_id}")

    now = datetime.now(timezone.utc)
    if action == "acknowledge":
        alert.status = "acknowledged"
        alert.acknowledged_at = now
        alert.assigned_to = uuid.UUID(staff_id)
    elif action == "resolve":
        alert.status = "resolved"
        alert.resolved_at = now
        alert.resolution_note = note
    elif action == "dismiss":
        alert.status = "dismissed"
        alert.resolved_at = now
        alert.resolution_note = note
    elif action == "escalate":
        alert.status = "open"
        alert.severity = "critical"
    else:
        raise ValueError(f"Unknown action: {action}")

    logger.info("Alert %s updated: action=%s by staff=%s", alert_id, action, staff_id)
    return {"alert_id": alert_id, "status": alert.status}


async def get_alerts(
    trial_id: str,
    status: str | None,
    severity: str | None,
    db: AsyncSession,
) -> list[dict]:
    """Get alerts for a trial with optional filtering."""
    # Get all patient_ids for this trial through sites
    sites = (await db.execute(
        select(Site).where(Site.trial_id == uuid.UUID(trial_id))
    )).scalars().all()
    site_ids = [s.id for s in sites]

    from app.models.patient import Patient
    patients = (await db.execute(
        select(Patient).where(Patient.site_id.in_(site_ids))
    )).scalars().all()
    patient_ids = [p.id for p in patients]

    conditions = [Alert.patient_id.in_(patient_ids)]
    if status:
        conditions.append(Alert.status == status)
    if severity:
        conditions.append(Alert.severity == severity)

    result = await db.execute(
        select(Alert)
        .where(and_(*conditions))
        .order_by(Alert.created_at.desc())
        .limit(100)
    )
    alerts = result.scalars().all()

    return [
        {
            "id": str(a.id),
            "patient_id": str(a.patient_id),
            "alert_type": a.alert_type,
            "severity": a.severity,
            "title": a.title,
            "description": a.description,
            "status": a.status,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "assigned_to": str(a.assigned_to) if a.assigned_to else None,
        }
        for a in alerts
    ]


async def _get_trial_id(patient_id: str, db: AsyncSession) -> str | None:
    """Get the trial_id for a patient (through site)."""
    from app.models.patient import Patient
    patient = (await db.execute(
        select(Patient).where(Patient.id == uuid.UUID(patient_id))
    )).scalars().first()
    if not patient:
        return None
    site = (await db.execute(
        select(Site).where(Site.id == patient.site_id)
    )).scalars().first()
    return str(site.trial_id) if site else None
