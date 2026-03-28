"""Symptom entry model with AI classification and CRC review fields."""

import uuid
from datetime import date, datetime

from sqlmodel import Field, SQLModel, Column
from sqlalchemy import Text, TIMESTAMP


class SymptomEntry(SQLModel, table=True):
    __tablename__ = "symptom_entries"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    patient_id: uuid.UUID = Field(foreign_key="patients.id")
    session_id: uuid.UUID | None = Field(default=None, foreign_key="checkin_sessions.id")
    symptom_text: str = Field(sa_column=Column(Text, nullable=False))
    meddra_pt_code: str | None = Field(default=None, max_length=20)
    meddra_pt_term: str | None = Field(default=None, max_length=255)
    meddra_soc: str | None = Field(default=None, max_length=255)
    severity_grade: int | None = None  # CTCAE v5: 1-5
    onset_date: date | None = None
    is_ongoing: bool = Field(default=True)
    resolution_date: date | None = None
    relationship: str | None = Field(default=None, max_length=30)
    # unrelated, unlikely, possible, probable, definite
    action_taken: str | None = Field(default=None, max_length=50)
    # none, dose_reduced, drug_interrupted, drug_discontinued
    ai_confidence: float | None = None  # 0.0-1.0
    crc_reviewed: bool = Field(default=False)
    crc_reviewed_at: datetime | None = Field(
        default=None, sa_column=Column(TIMESTAMP(timezone=True))
    )
    crc_reviewed_by: uuid.UUID | None = Field(default=None, foreign_key="staff.id")
    crc_override_term: str | None = Field(default=None, max_length=255)
    crc_override_grade: int | None = None
    is_sae: bool = Field(default=False)  # serious adverse event
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )
