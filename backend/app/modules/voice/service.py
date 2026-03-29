"""Voice check-in service — LiveKit room management and transcript persistence.

Handles creation of LiveKit rooms for voice check-in sessions, token
generation for patients and agents, and transcript retrieval from the
database.
"""

import json
import logging
import uuid

from livekit import api as livekit_api
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.checkin import CheckinMessage, CheckinSession
from app.models.patient import Patient
from app.models.trial import ProtocolConfig, Site

logger = logging.getLogger(__name__)


async def _get_protocol_context(patient_id: str, db: AsyncSession) -> dict:
    """Load protocol context for a patient's trial (used as room metadata)."""
    patient = (
        await db.execute(
            select(Patient).where(Patient.id == uuid.UUID(patient_id))
        )
    ).scalars().first()
    if not patient:
        logger.warning("Patient not found for voice context: %s", patient_id)
        return {}

    site = (
        await db.execute(select(Site).where(Site.id == patient.site_id))
    ).scalars().first()
    if not site:
        return {}

    config = (
        await db.execute(
            select(ProtocolConfig).where(ProtocolConfig.trial_id == site.trial_id)
        )
    ).scalars().first()

    return {
        "trial_id": str(site.trial_id),
        "protocol_number": site.site_number or "",
        "therapeutic_area": "oncology",
        "expected_side_effects": config.expected_side_effects if config else [],
    }


async def create_voice_room(
    patient_id: str,
    session_id: str,
    db: AsyncSession,
) -> dict:
    """Create a LiveKit room and generate a patient access token.

    The room is configured with metadata containing patient and protocol
    context so the voice agent can read it when it joins.
    """
    room_name = f"checkin-{session_id}"

    logger.info(
        "Creating voice room: room=%s, patient=%s, session=%s",
        room_name,
        patient_id,
        session_id,
    )

    # Load protocol context to embed in room metadata
    protocol_context = await _get_protocol_context(patient_id, db)
    room_metadata = json.dumps({
        "patient_id": patient_id,
        "session_id": session_id,
        "protocol_context": protocol_context,
    })

    # Create the room via LiveKit API with metadata
    lk_api = livekit_api.LiveKitAPI(
        url=settings.LIVEKIT_URL,
        api_key=settings.LIVEKIT_API_KEY,
        api_secret=settings.LIVEKIT_API_SECRET,
    )
    try:
        await lk_api.room.create_room(
            livekit_api.CreateRoomRequest(
                name=room_name,
                metadata=room_metadata,
            )
        )
        logger.info("LiveKit room created via API: %s", room_name)
    except Exception as exc:
        # Room may already exist or API may not be reachable in dev
        logger.warning("Could not create room via API (may already exist): %s", exc)
    finally:
        await lk_api.aclose()

    # Generate a LiveKit access token for the patient
    token = livekit_api.AccessToken(
        api_key=settings.LIVEKIT_API_KEY,
        api_secret=settings.LIVEKIT_API_SECRET,
    )
    token.with_identity(f"patient-{patient_id}")
    token.with_name("Patient")
    token.with_grants(
        livekit_api.VideoGrants(
            room_join=True,
            room=room_name,
        )
    )

    jwt_token = token.to_jwt()

    # Return the client-facing LiveKit URL (not the internal Docker hostname)
    livekit_url = settings.LIVEKIT_CLIENT_URL
    logger.info(
        "Voice room ready: room=%s, livekit_url=%s, token_issued=True",
        room_name,
        livekit_url,
    )

    return {
        "room_name": room_name,
        "livekit_url": livekit_url,
        "token": jwt_token,
        "session_id": session_id,
    }


async def get_agent_token(room_name: str) -> str:
    """Generate a LiveKit access token for the server-side voice agent."""
    token = livekit_api.AccessToken(
        api_key=settings.LIVEKIT_API_KEY,
        api_secret=settings.LIVEKIT_API_SECRET,
    )
    token.with_identity("checkin-agent")
    token.with_name("TrialPulse Health Assistant")
    token.with_grants(
        livekit_api.VideoGrants(
            room_join=True,
            room=room_name,
        )
    )
    return token.to_jwt()


async def save_voice_transcript(
    session_id: str,
    role: str,
    content: str,
    db: AsyncSession,
) -> None:
    """Persist a single transcript message from a voice check-in session.

    Called by the voice agent or transcript webhook to store messages
    in the same checkin_messages table used by text check-ins.
    """
    sid = uuid.UUID(session_id)

    # Determine next sequence number
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
        content=content,
        message_type="voice_transcript",
    )
    db.add(msg)
    await db.flush()
    logger.debug(
        "Saved voice transcript: session=%s, role=%s, seq=%d",
        session_id,
        role,
        next_seq,
    )


async def get_transcript(session_id: str, db: AsyncSession) -> list[dict]:
    """Retrieve the full transcript for a check-in session."""
    sid = uuid.UUID(session_id)
    query = (
        select(CheckinMessage)
        .where(CheckinMessage.session_id == sid)
        .order_by(CheckinMessage.sequence_number.asc())
    )
    result = await db.execute(query)
    messages = result.scalars().all()

    logger.debug("Retrieved %d transcript messages for session %s", len(messages), session_id)
    return [
        {
            "id": str(msg.id),
            "role": msg.role,
            "content": msg.content,
            "recorded_at": msg.created_at,
        }
        for msg in messages
    ]
