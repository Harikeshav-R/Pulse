"""Risk score calculation per TECHNICAL_DOC §8.2.

Four components: symptom (0-40), wearable (0-30), engagement (0-15), compliance (0-15).
Total score: 0-100. Tiers: low (0-30), medium (31-60), high (61-100).
"""

import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import RiskScore
from app.models.checkin import CheckinSession
from app.models.symptom import SymptomEntry
from app.models.wearable import WearableAnomaly

logger = logging.getLogger(__name__)


def _score_tier(score: int) -> str:
    if score <= 30:
        return "low"
    elif score <= 60:
        return "medium"
    return "high"


async def calculate_risk_score(
    patient_id: str,
    db: AsyncSession,
    lookback_days: int = 14,
) -> dict:
    """Calculate a comprehensive risk score for a patient."""
    pid = uuid.UUID(patient_id)
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    factors = []

    # ── Symptom component (0-40) ──
    symptoms_result = await db.execute(
        select(SymptomEntry)
        .where(SymptomEntry.patient_id == pid, SymptomEntry.created_at >= cutoff)
        .order_by(SymptomEntry.created_at.desc())
    )
    symptoms = symptoms_result.scalars().all()
    symptom_score = 0.0

    for s in symptoms:
        grade = s.severity_grade or 0
        if grade >= 3:
            symptom_score += 15
            factors.append(f"Grade {grade} {s.meddra_pt_term or 'symptom'}")
        elif grade == 2:
            symptom_score += 8
            factors.append(f"Grade {grade} {s.meddra_pt_term or 'symptom'}")
        elif grade == 1:
            symptom_score += 3

    # ── Symptom Worsening ──
    sessions_result = await db.execute(
        select(CheckinSession)
        .where(CheckinSession.patient_id == pid, CheckinSession.status == "completed")
        .order_by(CheckinSession.completed_at.desc())
        .limit(2)
    )
    last_two_sessions = sessions_result.scalars().all()
    if len(last_two_sessions) == 2:
        curr_session, prev_session = last_two_sessions[0], last_two_sessions[1]
        curr_syms = (await db.execute(select(SymptomEntry).where(SymptomEntry.session_id == curr_session.id))).scalars().all()
        prev_syms = (await db.execute(select(SymptomEntry).where(SymptomEntry.session_id == prev_session.id))).scalars().all()
        
        prev_map = {s.meddra_pt_term or s.symptom_text: (s.severity_grade or 0) for s in prev_syms}
        for cs in curr_syms:
            term = cs.meddra_pt_term or cs.symptom_text
            curr_grade = cs.severity_grade or 0
            if curr_grade > 0 and term in prev_map:
                prev_grade = prev_map[term]
                if curr_grade > prev_grade:
                    symptom_score += 15
                    factors.append(f"Worsening {term} ({prev_grade} -> {curr_grade})")

    symptom_score = min(symptom_score, 40)

    # ── Wearable component (0-30) ──
    anomalies_result = await db.execute(
        select(WearableAnomaly)
        .where(
            WearableAnomaly.patient_id == pid,
            WearableAnomaly.created_at >= cutoff,
            WearableAnomaly.resolved == False,
        )
    )
    anomalies = anomalies_result.scalars().all()
    wearable_score = 0.0
    for a in anomalies:
        if a.severity == "high":
            wearable_score += 15
            factors.append(f"{a.metric} anomaly (z={a.z_score or 'N/A'})")
        elif a.severity == "medium":
            wearable_score += 7
            factors.append(f"{a.metric} trend anomaly")
    wearable_score = min(wearable_score, 30)

    # ── Engagement component (0-15) ──
    last_active_result = await db.execute(
        select(CheckinSession)
        .where(CheckinSession.patient_id == pid, CheckinSession.status == "completed")
        .order_by(CheckinSession.completed_at.desc())
        .limit(1)
    )
    last_session = last_active_result.scalars().first()
    engagement_score = 0.0
    if last_session and last_session.completed_at:
        hours_since = (datetime.now(timezone.utc) - last_session.completed_at).total_seconds() / 3600
        if hours_since > 72:
            engagement_score = 15
            factors.append(f"No check-in for {int(hours_since/24)} days")
        elif hours_since > 48:
            engagement_score = 10
    else:
        engagement_score = 15
        factors.append("No completed check-ins")

    # ── Compliance component (0-15) ──
    total_sessions = await db.execute(
        select(func.count(CheckinSession.id))
        .where(CheckinSession.patient_id == pid, CheckinSession.started_at >= cutoff)
    )
    completed_sessions = await db.execute(
        select(func.count(CheckinSession.id))
        .where(
            CheckinSession.patient_id == pid,
            CheckinSession.started_at >= cutoff,
            CheckinSession.status == "completed",
        )
    )
    total = total_sessions.scalar() or 0
    completed = completed_sessions.scalar() or 0
    compliance_rate = completed / max(total, 1)
    if compliance_rate < 0.5:
        compliance_score = 20.0
        factors.append(f"{compliance_rate:.0%} check-in compliance (<50%)")
    else:
        compliance_score = 0.0

    # ── Total ──
    total_score = int(min(
        symptom_score + wearable_score + engagement_score + compliance_score, 100
    ))
    tier = _score_tier(total_score)

    # Save risk score record
    risk = RiskScore(
        patient_id=pid,
        score=total_score,
        tier=tier,
        symptom_component=symptom_score,
        wearable_component=wearable_score,
        engagement_component=engagement_score,
        compliance_component=compliance_score,
        contributing_factors=[{"factor": f, "weight": 0} for f in factors],
    )
    db.add(risk)
    await db.flush()

    from app.main import event_bus, ws_manager
    if event_bus:
        await event_bus.publish("risk_score.updated", {
            "patient_id": patient_id,
            "score": total_score,
            "tier": tier,
            "risk_id": str(risk.id),
        })

    logger.info(
        "Risk score calculated: patient=%s, score=%d (%s), factors=%d",
        patient_id, total_score, tier, len(factors),
    )
    return {
        "patient_id": patient_id,
        "score": total_score,
        "tier": tier,
        "components": {
            "symptom": symptom_score,
            "wearable": wearable_score,
            "engagement": engagement_score,
            "compliance": compliance_score,
        },
        "factors": factors,
    }
