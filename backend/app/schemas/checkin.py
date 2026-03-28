from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class StartCheckinRequest(BaseModel):
    session_type: str = "scheduled"
    modality: str = "text"


class SendMessageRequest(BaseModel):
    content: str
    message_type: str = "text"


class CheckinResponse(BaseModel):
    session_id: str
    message: str
    session_complete: bool = False


class CheckinHistoryItem(BaseModel):
    session_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    modality: str
    symptoms_count: int = 0
    overall_feeling: Optional[int] = None


class CheckinHistoryResponse(BaseModel):
    sessions: list[CheckinHistoryItem]
    total: int
