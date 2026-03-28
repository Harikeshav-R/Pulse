"""Alert and risk score models."""

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel, Column
from sqlalchemy import Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB


class Alert(SQLModel, table=True):
    __tablename__ = "alerts"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    patient_id: uuid.UUID = Field(foreign_key="patients.id")
    alert_type: str = Field(max_length=30)
    # symptom_severe, symptom_new, wearable_anomaly, missed_checkin,
    # engagement_decline, risk_score_elevated, sae_reported
    severity: str = Field(max_length=10)  # low, medium, high, critical
    title: str = Field(sa_column=Column(Text, nullable=False))
    description: str = Field(sa_column=Column(Text, nullable=False))
    source_type: str | None = Field(default=None, max_length=30)
    source_id: uuid.UUID | None = None
    status: str = Field(default="open", max_length=20)
    # open, acknowledged, in_progress, resolved, dismissed
    assigned_to: uuid.UUID | None = Field(default=None, foreign_key="staff.id")
    acknowledged_at: datetime | None = Field(
        default=None, sa_column=Column(TIMESTAMP(timezone=True))
    )
    resolved_at: datetime | None = Field(
        default=None, sa_column=Column(TIMESTAMP(timezone=True))
    )
    resolution_note: str | None = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )


class RiskScore(SQLModel, table=True):
    __tablename__ = "risk_scores"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    patient_id: uuid.UUID = Field(foreign_key="patients.id")
    score: int  # 0-100
    tier: str = Field(max_length=10)  # low, medium, high
    symptom_component: float  # 0-40
    wearable_component: float  # 0-30
    engagement_component: float  # 0-15
    compliance_component: float  # 0-15
    contributing_factors: list = Field(default=[], sa_column=Column(JSONB, nullable=False))
    calculated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )
