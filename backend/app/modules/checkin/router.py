"""Check-in API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from app.deps import get_db, get_current_patient, get_event_bus
from app.modules.checkin.service import start_checkin, process_message

logger = logging.getLogger(__name__)
router = APIRouter(tags=["checkin"])


# ─── Request/Response schemas ───


class StartCheckinRequest(SQLModel):
    session_type: str = "scheduled"
    modality: str = "text"


class SendMessageRequest(SQLModel):
    content: str
    message_type: str = "text"


class CheckinResponse(SQLModel):
    session_id: str
    message: str
    session_complete: bool = False


# ─── Endpoints ───


@router.post("/checkins/start", response_model=CheckinResponse)
async def start_checkin_endpoint(
    body: StartCheckinRequest,
    patient: dict = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
):
    """Start a new check-in session."""
    try:
        result = await start_checkin(
            patient_id=patient["patient_id"],
            session_type=body.session_type,
            modality=body.modality,
            db=db,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/checkins/{session_id}/message", response_model=CheckinResponse)
async def send_message_endpoint(
    session_id: str,
    body: SendMessageRequest,
    patient: dict = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
    event_bus=Depends(get_event_bus),
):
    """Send a message in an active check-in session."""
    try:
        result = await process_message(
            session_id=session_id,
            content=body.content,
            message_type=body.message_type,
            db=db,
            event_bus=event_bus,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
