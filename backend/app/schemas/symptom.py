from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional


class SymptomDetail(BaseModel):
    id: str
    symptom_text: str
    meddra_pt_term: Optional[str] = None
    severity_grade: Optional[int] = None
    onset_date: Optional[date] = None
    is_ongoing: bool = True
    created_at: datetime
    ai_confidence: Optional[float] = None
    crc_reviewed: bool = False
    crc_reviewed_by: Optional[str] = None
    crc_reviewed_at: Optional[datetime] = None


class SymptomHistoryResponse(BaseModel):
    symptoms: list[SymptomDetail]


class SymptomReviewRequest(BaseModel):
    action: str  # "confirm" or "override"
    override_term: Optional[str] = None
    override_grade: Optional[int] = None
    notes: Optional[str] = None


class SymptomReviewResponse(BaseModel):
    symptom_id: str
    crc_reviewed: bool
    reviewed_at: datetime
    reviewed_by: str
