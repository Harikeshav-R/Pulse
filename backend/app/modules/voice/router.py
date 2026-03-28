"""Voice check-in API endpoints."""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from app.deps import get_db, get_current_patient
from app.modules.checkin.service import start_checkin
from app.modules.voice.service import create_voice_room

logger = logging.getLogger(__name__)
router = APIRouter(tags=["voice"])


class VoiceSessionResponse(SQLModel):
    session_id: str
    room_name: str
    livekit_url: str
    token: str


@router.post("/voice/start", response_model=VoiceSessionResponse)
async def start_voice_checkin(
    patient: dict = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
):
    """Start a voice check-in session.

    Creates a check-in session (modality=voice) and a LiveKit room,
    then returns the room URL and access token for the patient to join.
    """
    # Create the check-in session
    session = await start_checkin(
        patient_id=patient["patient_id"],
        session_type="scheduled",
        modality="voice",
        db=db,
    )
    session_id = session["session_id"]

    # Create the LiveKit voice room
    room = await create_voice_room(patient["patient_id"], session_id)

    logger.info(
        "Voice check-in started: session_id=%s, room=%s",
        session_id, room["room_name"],
    )

    return VoiceSessionResponse(
        session_id=session_id,
        room_name=room["room_name"],
        livekit_url=room["livekit_url"],
        token=room["token"],
    )
