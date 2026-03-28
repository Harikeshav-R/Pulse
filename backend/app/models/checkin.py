"""Check-in session and message models."""

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel, Column
from sqlalchemy import Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB


class CheckinSession(SQLModel, table=True):
    __tablename__ = "checkin_sessions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    patient_id: uuid.UUID = Field(foreign_key="patients.id")
    session_type: str = Field(default="scheduled", max_length=20)  # scheduled, ad_hoc
    modality: str = Field(default="text", max_length=10)  # text, voice
    status: str = Field(default="in_progress", max_length=20)  # in_progress, completed, abandoned
    started_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )
    completed_at: datetime | None = Field(
        default=None,
        sa_column=Column(TIMESTAMP(timezone=True)),
    )
    duration_seconds: int | None = None
    overall_feeling: int | None = None  # 1-5 scale
    voice_room_id: str | None = Field(default=None, max_length=255)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )


class CheckinMessage(SQLModel, table=True):
    __tablename__ = "checkin_messages"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    session_id: uuid.UUID = Field(foreign_key="checkin_sessions.id")
    sequence_number: int
    role: str = Field(max_length=10)  # ai, patient
    content: str = Field(sa_column=Column(Text, nullable=False))
    message_type: str = Field(default="text", max_length=20)
    # text, quick_reply, scale_rating, date_picker, multi_select, voice_transcript
    quick_replies: list | None = Field(default=None, sa_column=Column(JSONB))
    selected_reply: str | None = Field(default=None, max_length=255)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )
