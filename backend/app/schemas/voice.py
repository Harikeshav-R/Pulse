from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VoiceSessionResponse(BaseModel):
    session_id: str
    room_name: str
    livekit_url: str
    token: str

class TranscriptMessage(BaseModel):
    id: str
    role: str
    content: str
    recorded_at: Optional[datetime] = None

class TranscriptResponse(BaseModel):
    messages: list[TranscriptMessage]
