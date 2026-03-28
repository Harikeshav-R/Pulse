import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.patient import Patient
from app.models.trial import Site, Trial, ProtocolConfig
from app.models.wearable import WearableConnection
from app.models.checkin import CheckinSession
from app.models.symptom import SymptomEntry
from app.schemas.patient import PatientProfileResponse
from app.schemas.checkin import CheckinHistoryResponse, CheckinHistoryItem
from app.schemas.symptom import SymptomHistoryResponse, SymptomDetail

logger = logging.getLogger(__name__)


async def get_patient_profile(patient_id: str, db: AsyncSession) -> PatientProfileResponse:
    query = (
        select(Patient, Site, Trial, ProtocolConfig)
        .join(Site, Patient.site_id == Site.id)
        .join(Trial, Site.trial_id == Trial.id)
        .join(ProtocolConfig, ProtocolConfig.trial_id == Trial.id)
        .where(Patient.id == patient_id)
    )
    result = await db.execute(query)
    row = result.first()
    if not row:
        raise ValueError("Patient not found")

    patient, site, trial, protocol_config = row

    wearable_query = select(WearableConnection).where(
        WearableConnection.patient_id == patient_id, WearableConnection.is_active.is_(True)
    )
    wearable_result = await db.execute(wearable_query)
    wearable = wearable_result.scalars().first()

    return PatientProfileResponse(
        patient_id=str(patient.id),
        subject_id=patient.subject_id,
        trial_name=trial.trial_title,
        site_name=site.site_name,
        enrollment_date=patient.enrollment_date,
        checkin_frequency=protocol_config.checkin_frequency,
        wearable_connected=wearable is not None,
    )


async def get_checkin_history(
    patient_id: str, limit: int, offset: int, db: AsyncSession
) -> CheckinHistoryResponse:
    count_query = select(func.count(CheckinSession.id)).where(
        CheckinSession.patient_id == patient_id
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = (
        select(CheckinSession)
        .where(CheckinSession.patient_id == patient_id)
        .order_by(CheckinSession.started_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(query)
    sessions = result.scalars().all()

    session_items = []
    for session in sessions:
        s_query = select(func.count(SymptomEntry.id)).where(SymptomEntry.session_id == session.id)
        s_count_result = await db.execute(s_query)
        s_count = s_count_result.scalar() or 0

        session_items.append(
            CheckinHistoryItem(
                session_id=str(session.id),
                started_at=session.started_at,
                completed_at=session.completed_at,
                modality=session.modality,
                symptoms_count=s_count,
                overall_feeling=session.overall_feeling,
            )
        )

    return CheckinHistoryResponse(sessions=session_items, total=total)


async def get_symptom_history(
    patient_id: str, limit: int, offset: int, db: AsyncSession
) -> SymptomHistoryResponse:
    query = (
        select(SymptomEntry)
        .where(SymptomEntry.patient_id == patient_id)
        .order_by(SymptomEntry.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(query)
    symptoms = result.scalars().all()

    items = []
    for s in symptoms:
        items.append(
            SymptomDetail(
                id=str(s.id),
                symptom_text=s.symptom_text,
                meddra_pt_term=s.meddra_pt_term,
                severity_grade=s.severity_grade,
                onset_date=s.onset_date,
                is_ongoing=s.is_ongoing,
                created_at=s.created_at,
                ai_confidence=s.ai_confidence,
                crc_reviewed=s.crc_reviewed,
                crc_reviewed_by=str(s.crc_reviewed_by) if s.crc_reviewed_by else None,
                crc_reviewed_at=s.crc_reviewed_at,
            )
        )

    return SymptomHistoryResponse(symptoms=items)
