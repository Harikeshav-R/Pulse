"""Check-in service — orchestrates patient symptom journal conversations.

Uses LangGraph for multi-step check-in orchestration and symptom classification.
"""

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.graphs.checkin_graph import build_checkin_graph, CheckinState
from app.ai.graphs.classifier_graph import build_classifier_graph
from app.ai.schemas import ClassificationResult
from app.models.checkin import CheckinSession, CheckinMessage
from app.models.symptom import SymptomEntry
from app.models.patient import Patient
from app.models.trial import ProtocolConfig, Site

logger = logging.getLogger(__name__)


async def _get_protocol_context(patient_id: str, db: AsyncSession) -> dict:
    """Load protocol context for a patient's trial."""
    patient = (await db.execute(
        select(Patient).where(Patient.id == uuid.UUID(patient_id))
    )).scalars().first()
    if not patient:
        raise ValueError(f"Patient not found: {patient_id}")

    site = (await db.execute(
        select(Site).where(Site.id == patient.site_id)
    )).scalars().first()

    config = (await db.execute(
        select(ProtocolConfig).where(ProtocolConfig.trial_id == site.trial_id)
    )).scalars().first()

    return {
        "trial_id": str(site.trial_id),
        "protocol_number": site.site_number if site else "",
        "therapeutic_area": "oncology",
        "expected_side_effects": config.expected_side_effects if config else [],
        "symptom_questions": config.symptom_questions if config else [],
    }


async def start_checkin(
    patient_id: str,
    session_type: str,
    modality: str,
    db: AsyncSession,
) -> dict:
    """Start a new check-in session and generate the first AI message."""
    logger.info(
        "Starting check-in: patient_id=%s, type=%s, modality=%s",
        patient_id, session_type, modality,
    )

    protocol_context = await _get_protocol_context(patient_id, db)

    session = CheckinSession(
        patient_id=uuid.UUID(patient_id),
        session_type=session_type,
        modality=modality,
        status="in_progress",
    )
    db.add(session)
    await db.flush()

    # Run the first step of the LangGraph check-in
    graph = build_checkin_graph()
    initial_state: CheckinState = {
        "messages": [{"role": "user", "content": "Start check-in"}],
        "phase": "greeting",
        "overall_feeling": None,
        "reported_symptoms": [],
        "protocol_context": protocol_context,
        "session_complete": False,
        "ai_response": "",
    }

    result = await graph.ainvoke(initial_state)
    greeting = result.get("ai_response", "Hi! How are you feeling today?")

    # Save the AI greeting message
    msg = CheckinMessage(
        session_id=session.id,
        sequence_number=1,
        role="ai",
        content=greeting,
        message_type="text",
    )
    db.add(msg)

    logger.info("Check-in started: session_id=%s", session.id)
    return {
        "session_id": str(session.id),
        "message": greeting,
        "session_complete": False,
    }


async def process_message(
    session_id: str,
    content: str,
    message_type: str,
    db: AsyncSession,
    event_bus=None,
) -> dict:
    """Process a patient message and generate the next AI response."""
    logger.info("Processing message: session_id=%s, type=%s", session_id, message_type)

    session = (await db.execute(
        select(CheckinSession).where(CheckinSession.id == uuid.UUID(session_id))
    )).scalars().first()
    if not session:
        raise ValueError(f"Session not found: {session_id}")

    # Load conversation history
    messages_result = await db.execute(
        select(CheckinMessage)
        .where(CheckinMessage.session_id == session.id)
        .order_by(CheckinMessage.sequence_number)
    )
    history = messages_result.scalars().all()
    next_seq = len(history) + 1

    # Save patient message
    patient_msg = CheckinMessage(
        session_id=session.id,
        sequence_number=next_seq,
        role="patient",
        content=content,
        message_type=message_type,
    )
    db.add(patient_msg)
    await db.flush()

    # Build message history for the LangGraph agent
    agent_messages = []
    for msg in history:
        role = "assistant" if msg.role == "ai" else "user"
        agent_messages.append({"role": role, "content": msg.content})
    agent_messages.append({"role": "user", "content": content})

    # Get protocol context and run the LangGraph
    protocol_context = await _get_protocol_context(str(session.patient_id), db)
    graph = build_checkin_graph()

    state: CheckinState = {
        "messages": agent_messages,
        "phase": "symptom_screening",  # The graph will determine the right phase
        "overall_feeling": None,
        "reported_symptoms": [],
        "protocol_context": protocol_context,
        "session_complete": False,
        "ai_response": "",
    }

    result = await graph.ainvoke(state)
    ai_content = result.get("ai_response", "Thank you for sharing that. Is there anything else?")
    session_complete = result.get("session_complete", False)

    # Save AI response
    ai_msg = CheckinMessage(
        session_id=session.id,
        sequence_number=next_seq + 1,
        role="ai",
        content=ai_content,
        message_type="text",
    )
    db.add(ai_msg)

    # On completion: classify symptoms via the classifier LangGraph
    if session_complete:
        session.status = "completed"
        session.completed_at = datetime.now(timezone.utc)
        if session.started_at:
            session.duration_seconds = int(
                (session.completed_at - session.started_at).total_seconds()
            )
        await _classify_and_publish(session, db, protocol_context, event_bus)
        logger.info("Check-in completed: session_id=%s", session.id)

    return {
        "session_id": str(session.id),
        "message": ai_content,
        "session_complete": session_complete,
    }


async def _classify_and_publish(
    session: CheckinSession,
    db: AsyncSession,
    protocol_context: dict,
    event_bus=None,
) -> None:
    """Run structured symptom classification via the classifier LangGraph."""
    logger.info("Classifying symptoms for session: %s", session.id)

    # Load full conversation
    messages_result = await db.execute(
        select(CheckinMessage)
        .where(CheckinMessage.session_id == session.id)
        .order_by(CheckinMessage.sequence_number)
    )
    messages = messages_result.scalars().all()
    conversation_text = "\n".join(
        f"{'AI' if m.role == 'ai' else 'Patient'}: {m.content}" for m in messages
    )

    # Run classifier LangGraph — returns validated ClassificationResult
    classifier = build_classifier_graph()
    result = await classifier.ainvoke({
        "conversation_text": conversation_text,
        "protocol_context": protocol_context,
        "classification": None,
        "is_validated": False,
    })

    classification: ClassificationResult | None = result.get("classification")
    if not classification:
        logger.warning("Classifier returned no result for session %s", session.id)
        return

    # Create SymptomEntry records from validated Pydantic models
    for symptom in classification.symptoms:
        entry = SymptomEntry(
            patient_id=session.patient_id,
            session_id=session.id,
            symptom_text=symptom.symptom_text,
            meddra_pt_code=symptom.meddra_pt_code,
            meddra_pt_term=symptom.meddra_pt_term,
            meddra_soc=symptom.meddra_soc,
            severity_grade=symptom.severity_ctcae,
            ai_confidence=symptom.confidence,
            is_ongoing=symptom.is_ongoing,
        )
        db.add(entry)
        await db.flush()

        if event_bus:
            await event_bus.publish("symptom.reported", {
                "patient_id": str(session.patient_id),
                "symptom_entry_id": str(entry.id),
                "session_id": str(session.id),
                "meddra_pt_term": entry.meddra_pt_term,
                "severity_grade": entry.severity_grade,
                "ai_confidence": entry.ai_confidence,
                "is_sae": entry.is_sae,
            })

    logger.info(
        "Classified %d symptoms (severe=%s) for session %s",
        classification.total_symptoms,
        classification.has_severe_symptoms,
        session.id,
    )
