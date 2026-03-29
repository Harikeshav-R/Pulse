from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PatientListItem(BaseModel):
    patient_id: str
    subject_id: str
    treatment_arm: Optional[str] = None
    risk_score: Optional[int] = None
    risk_tier: Optional[str] = None
    last_checkin_at: Optional[datetime] = None
    open_alerts: int = 0
    latest_symptom: Optional[str] = None
    wearable_status: bool = False


class PatientListResponse(BaseModel):
    patients: list[PatientListItem]
    total: int
    page: int


class PatientTimelineEvent(BaseModel):
    type: str  # e.g., 'checkin', 'symptom', 'alert', 'wearable_anomaly'
    timestamp: datetime
    title: str
    details: str
    severity: Optional[str] = None


class PatientTimelineResponse(BaseModel):
    events: list[PatientTimelineEvent]


class DataPoint(BaseModel):
    timestamp: datetime
    value: float


class BaselineData(BaseModel):
    mean: float
    stddev: float


class PatientWearableDataResponse(BaseModel):
    data_points: list[DataPoint]
    baseline: Optional[BaselineData] = None
    anomalies: list[dict]


class CheckinMessageItem(BaseModel):
    id: str
    role: str
    content: str
    message_type: str
    created_at: datetime


class CheckinSessionItem(BaseModel):
    session_id: str
    modality: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    messages: list[CheckinMessageItem]


class PatientCheckinsResponse(BaseModel):
    sessions: list[CheckinSessionItem]
    total: int
