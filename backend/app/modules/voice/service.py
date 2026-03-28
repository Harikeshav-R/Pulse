"""LiveKit + Gemini Live voice check-in agent.

Uses livekit-plugins-google for native Gemini Live voice interaction
per TECHNICAL_DOC §5.3 and user requirements.
"""

import logging
import uuid

from livekit import api as livekit_api

from app.config import settings

logger = logging.getLogger(__name__)


async def create_voice_room(patient_id: str, session_id: str) -> dict:
    """Create a LiveKit room and generate a patient access token.

    The LiveKit room hosts the voice check-in session. A server-side
    voice agent (Gemini Live) joins the room to conduct the check-in.
    """
    room_name = f"checkin-{session_id}"

    logger.info(
        "Creating voice room: room=%s, patient=%s, session=%s",
        room_name, patient_id, session_id,
    )

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
    logger.info("Voice room created: room=%s, token_issued=True", room_name)

    return {
        "room_name": room_name,
        "livekit_url": settings.LIVEKIT_URL.replace("ws://", "wss://").replace(
            "localhost", settings.LIVEKIT_URL.split("://")[-1].split(":")[0]
        ),
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
