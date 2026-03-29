"""LiveKit voice agent worker — Gemini Live powered check-in agent.

Uses livekit-agents >= 1.0 with livekit-plugins-google for native
Gemini Live audio-to-audio conversation. The agent joins a LiveKit room,
listens to patient speech, and responds via Gemini's realtime voice API.

Per TECHNICAL_DOC §5.4, the voice pipeline:
  Patient mic → LiveKit room → Gemini Live (audio-in, audio-out) → Patient speaker

Transcript persistence and symptom classification are handled by hooking
into the agent session's transcript events and writing to PostgreSQL
after the session ends.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone

from livekit.agents import (
    Agent,
    AgentSession,
    AutoSubscribe,
    JobContext,
    RunContext,
    WorkerOptions,
    cli,
)
from livekit.plugins import google
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.ai.graphs.classifier_graph import build_classifier_graph
from app.ai.prompts.checkin_system import CHECKIN_SYSTEM_PROMPT
from app.ai.schemas import ClassificationResult
from app.config import settings
from app.models.checkin import CheckinMessage, CheckinSession
from app.models.symptom import SymptomEntry

logger = logging.getLogger(__name__)

# Standalone DB session factory for the worker process (not shared with FastAPI)
_engine = create_async_engine(settings.DATABASE_URL, pool_size=5, max_overflow=5)
_session_factory = async_sessionmaker(_engine, expire_on_commit=False)


class VoiceCheckinAgent(Agent):
    """Voice check-in agent using Gemini Live via LiveKit.

    Subclasses the livekit-agents Agent base class with clinical trial
    check-in instructions. The agent conducts a voice-based symptom
    check-in conversation using the same prompt template as the text chat.
    """

    def __init__(self, protocol_context: dict | None = None):
        ctx = protocol_context or {}
        instructions = CHECKIN_SYSTEM_PROMPT.format(
            therapeutic_area=ctx.get("therapeutic_area", "clinical"),
            protocol_number=ctx.get("protocol_number", ""),
            expected_side_effects=str(ctx.get("expected_side_effects", [])),
            phase="voice check-in",
        )
        super().__init__(instructions=instructions)
        self.protocol_context = ctx
        logger.info(
            "VoiceCheckinAgent created: protocol=%s",
            ctx.get("protocol_number", "unknown"),
        )


def _parse_room_metadata(ctx: JobContext) -> dict:
    """Extract patient and protocol info from LiveKit room metadata."""
    raw = ctx.room.metadata
    if not raw:
        logger.warning("Room %s has no metadata, using defaults", ctx.room.name)
        return {}
    try:
        meta = json.loads(raw)
        logger.debug(
            "Parsed room metadata: patient_id=%s, room=%s",
            meta.get("patient_id", "?"),
            ctx.room.name,
        )
        return meta
    except (json.JSONDecodeError, TypeError) as exc:
        logger.error("Failed to parse room metadata for %s: %s", ctx.room.name, exc)
        return {}


async def _save_transcript_message(session_id: str, role: str, content: str) -> None:
    """Persist a single transcript message to the database."""
    if not content or not content.strip():
        return
    async with _session_factory() as db:
        sid = uuid.UUID(session_id)
        # Get next sequence number
        from sqlalchemy import select

        result = await db.execute(
            select(CheckinMessage)
            .where(CheckinMessage.session_id == sid)
            .order_by(CheckinMessage.sequence_number.desc())
        )
        last_msg = result.scalars().first()
        next_seq = (last_msg.sequence_number + 1) if last_msg else 1

        msg = CheckinMessage(
            session_id=sid,
            sequence_number=next_seq,
            role=role,
            content=content.strip(),
            message_type="voice_transcript",
        )
        db.add(msg)
        await db.commit()
        logger.debug("Saved voice transcript: session=%s, role=%s, seq=%d", session_id, role, next_seq)


async def _classify_and_store(session_id: str, patient_id: str, protocol_context: dict) -> None:
    """Run symptom classification on the full voice transcript and store results."""
    logger.info("Running symptom classification for voice session: %s", session_id)
    async with _session_factory() as db:
        from sqlalchemy import select

        sid = uuid.UUID(session_id)
        pid = uuid.UUID(patient_id)

        # Load full transcript
        result = await db.execute(
            select(CheckinMessage)
            .where(CheckinMessage.session_id == sid)
            .order_by(CheckinMessage.sequence_number)
        )
        messages = result.scalars().all()
        if not messages:
            logger.warning("No transcript messages for session %s, skipping classification", session_id)
            return

        conversation_text = "\n".join(
            f"{'AI' if m.role == 'ai' else 'Patient'}: {m.content}" for m in messages
        )

        # Run classifier LangGraph
        classifier = build_classifier_graph()
        cls_result = await classifier.ainvoke({
            "conversation_text": conversation_text,
            "protocol_context": protocol_context,
            "classification": None,
            "is_validated": False,
        })

        classification: ClassificationResult | None = cls_result.get("classification")
        if not classification:
            logger.warning("Classifier returned no result for voice session %s", session_id)
            return

        # Store symptom entries
        for symptom in classification.symptoms:
            entry = SymptomEntry(
                patient_id=pid,
                session_id=sid,
                symptom_text=symptom.symptom_text,
                meddra_pt_code=symptom.meddra_pt_code,
                meddra_pt_term=symptom.meddra_pt_term,
                meddra_soc=symptom.meddra_soc,
                severity_grade=symptom.severity_ctcae,
                ai_confidence=symptom.confidence,
                is_ongoing=symptom.is_ongoing,
            )
            db.add(entry)

        # Mark session as completed
        session = (
            await db.execute(select(CheckinSession).where(CheckinSession.id == sid))
        ).scalars().first()
        if session:
            session.status = "completed"
            session.completed_at = datetime.now(timezone.utc)
            if session.started_at:
                session.duration_seconds = int(
                    (session.completed_at - session.started_at).total_seconds()
                )

        await db.commit()
        logger.info(
            "Voice classification complete: session=%s, symptoms=%d, severe=%s",
            session_id,
            classification.total_symptoms,
            classification.has_severe_symptoms,
        )


async def entrypoint(ctx: JobContext):
    """LiveKit agent entrypoint — called when a patient joins a voice room.

    Connects to the room, creates a Gemini Live realtime model, starts the
    agent session, and hooks up transcript persistence + classification.
    """
    logger.info("Voice agent entrypoint called: room=%s", ctx.room.name)

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    logger.info("Connected to room: %s", ctx.room.name)

    # Parse patient/protocol context from room metadata
    meta = _parse_room_metadata(ctx)
    protocol_context = meta.get("protocol_context", {})
    session_id = meta.get("session_id")
    patient_id = meta.get("patient_id")

    # Create Gemini Live realtime model — native audio-to-audio
    model = google.beta.realtime.RealtimeModel(
        model="gemini-2.5-flash-native-audio-preview-12-2025",
        # model="gemini-2.0-flash-exp",
        # voice="Puck",
        temperature=0.7,
        api_key=settings.GOOGLE_API_KEY,
    )

    agent = VoiceCheckinAgent(protocol_context=protocol_context)
    session = AgentSession(llm=model)

    # Hook transcript persistence into session events.
    # LiveKit's event emitter requires synchronous callbacks — use create_task.
    if session_id:

        @session.on("agent_speech_committed")
        def on_agent_speech(text: str):
            asyncio.create_task(_save_transcript_message(session_id, "ai", text))

        @session.on("user_speech_committed")
        def on_user_speech(text: str):
            asyncio.create_task(_save_transcript_message(session_id, "patient", text))

    logger.info(
        "Starting voice agent session: room=%s, patient_id=%s",
        ctx.room.name,
        patient_id or "unknown",
    )

    await session.start(room=ctx.room, agent=agent)
    logger.info("Voice agent session active: room=%s", ctx.room.name)

    # Prompt the agent to greet the patient first
    await session.generate_reply()

    # Wait for the session to end (participant disconnect), then classify
    @ctx.room.on("participant_disconnected")
    def on_participant_left(participant):
        if participant.identity.startswith("patient-") and session_id and patient_id:
            logger.info(
                "Patient disconnected, running classification: session=%s",
                session_id,
            )
            asyncio.create_task(
                _classify_and_store(session_id, patient_id, protocol_context)
            )


def run_voice_worker():
    """Entry point to run the LiveKit voice agent as a standalone worker."""
    logger.info("Starting voice agent worker: livekit_url=%s", settings.LIVEKIT_URL)
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            api_key=settings.LIVEKIT_API_KEY,
            api_secret=settings.LIVEKIT_API_SECRET,
            ws_url=settings.LIVEKIT_URL,
        )
    )
