"""Trial, protocol configuration, and site models."""

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel, Column
from sqlalchemy import Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB


class Trial(SQLModel, table=True):
    __tablename__ = "trials"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    sponsor_name: str = Field(max_length=255)
    protocol_number: str = Field(max_length=100, unique=True)
    trial_title: str = Field(sa_column=Column(Text, nullable=False))
    therapeutic_area: str = Field(max_length=100)
    phase: str = Field(max_length=10)
    status: str = Field(default="active", max_length=20)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )


class ProtocolConfig(SQLModel, table=True):
    __tablename__ = "protocol_config"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    trial_id: uuid.UUID = Field(foreign_key="trials.id")
    checkin_frequency: str = Field(default="daily", max_length=20)
    checkin_window_hours: int = Field(default=24)
    expected_side_effects: dict | list = Field(default=[], sa_column=Column(JSONB, nullable=False))
    symptom_questions: list = Field(default=[], sa_column=Column(JSONB, nullable=False))
    wearable_required: bool = Field(default=False)
    wearable_metrics: list = Field(
        default=["heart_rate", "steps", "sleep"],
        sa_column=Column(JSONB, nullable=False),
    )
    alert_thresholds: dict = Field(default={}, sa_column=Column(JSONB, nullable=False))
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )


class Site(SQLModel, table=True):
    __tablename__ = "sites"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    trial_id: uuid.UUID = Field(foreign_key="trials.id")
    site_number: str = Field(max_length=50)
    site_name: str = Field(max_length=255)
    country: str = Field(max_length=100)
    timezone: str = Field(default="UTC", max_length=50)
    status: str = Field(default="active", max_length=20)
