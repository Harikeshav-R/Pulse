"""Voice check-in API endpoints.

Provides endpoints for starting voice check-in sessions (creates LiveKit
rooms with tokens) and fetching session transcripts.
"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_current_patient, get_current_staff
from app.modules.checkin.service import start_checkin
from app.modules.voice.service import create_voice_room, get_transcript
from app.schemas.voice import VoiceSessionResponse, TranscriptResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["voice"])


@router.post("/voice/start", response_model=VoiceSessionResponse)
async def start_voice_checkin(
    patient: dict = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
):
    """Start a voice check-in session.

    Creates a check-in session with modality='voice', then provisions
    a LiveKit room with room metadata containing patient and protocol
    context. Returns the room URL and access token for the mobile app
    to join.
    """
    patient_id = patient["patient_id"]

    # Create the check-in session record
    session = await start_checkin(
        patient_id=patient_id,
        session_type="scheduled",
        modality="voice",
        db=db,
    )
    session_id = session["session_id"]

    # Create the LiveKit voice room with metadata
    room = await create_voice_room(
        patient_id=patient_id,
        session_id=session_id,
        db=db,
    )

    logger.info(
        "Voice check-in started: session_id=%s, room=%s, patient_id=%s",
        session_id,
        room["room_name"],
        patient_id,
    )

    return VoiceSessionResponse(
        session_id=session_id,
        room_name=room["room_name"],
        livekit_url=room["livekit_url"],
        token=room["token"],
    )


@router.get("/voice/transcript/{session_id}", response_model=TranscriptResponse)
async def fetch_transcript(
    session_id: str,
    staff: dict = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    """Fetch the chronological message transcript of a voice/text check-in session."""
    logger.debug("Fetching transcript: session_id=%s, staff_id=%s", session_id, staff.get("staff_id"))
    messages = await get_transcript(session_id, db)
    return TranscriptResponse(messages=messages)
