"""Patient and patient app account models."""

import uuid
from datetime import date, datetime

from sqlmodel import Field, SQLModel, Column
from sqlalchemy import TIMESTAMP


class Patient(SQLModel, table=True):
    __tablename__ = "patients"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    site_id: uuid.UUID = Field(foreign_key="sites.id")
    enrollment_code: str = Field(max_length=50, unique=True)
    subject_id: str = Field(max_length=50)
    treatment_arm: str | None = Field(default=None, max_length=50)
    enrollment_date: date
    status: str = Field(default="enrolled", max_length=20)
    app_registered: bool = Field(default=False)
    wearable_connected: bool = Field(default=False)
    timezone: str = Field(default="UTC", max_length=50)
    language: str = Field(default="en", max_length=10)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )


class PatientAppAccount(SQLModel, table=True):
    __tablename__ = "patient_app_accounts"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    patient_id: uuid.UUID = Field(foreign_key="patients.id", unique=True)
    device_token: str | None = None
    device_platform: str | None = Field(default=None, max_length=10)
    device_model: str | None = Field(default=None, max_length=100)
    app_version: str | None = Field(default=None, max_length=20)
    last_active_at: datetime | None = None
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )
