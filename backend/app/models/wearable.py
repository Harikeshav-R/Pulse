"""Wearable data models: connections, readings, baselines, and anomalies."""

import uuid
from datetime import date, datetime

from sqlmodel import Field, SQLModel, Column
from sqlalchemy import TIMESTAMP


class WearableConnection(SQLModel, table=True):
    __tablename__ = "wearable_connections"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    patient_id: uuid.UUID = Field(foreign_key="patients.id")
    platform: str = Field(max_length=20)  # apple_healthkit, google_health_connect, fitbit
    device_name: str | None = Field(default=None, max_length=255)
    device_model: str | None = Field(default=None, max_length=255)
    last_sync_at: datetime | None = Field(
        default=None, sa_column=Column(TIMESTAMP(timezone=True))
    )
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )


class WearableReading(SQLModel, table=True):
    __tablename__ = "wearable_readings"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    patient_id: uuid.UUID = Field(foreign_key="patients.id")
    metric: str = Field(max_length=50)  # heart_rate, resting_heart_rate, steps, sleep_minutes, spo2
    value: float
    source: str | None = Field(default=None, max_length=50)
    quality: str = Field(default="raw", max_length=20)  # raw, hourly_avg, daily_avg
    recorded_at: datetime = Field(sa_column=Column(TIMESTAMP(timezone=True), nullable=False))
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )


class WearableBaseline(SQLModel, table=True):
    __tablename__ = "wearable_baselines"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    patient_id: uuid.UUID = Field(foreign_key="patients.id")
    metric: str = Field(max_length=50)
    baseline_mean: float
    baseline_stddev: float
    baseline_min: float | None = None
    baseline_max: float | None = None
    sample_count: int
    baseline_start: date
    baseline_end: date
    is_current: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )


class WearableAnomaly(SQLModel, table=True):
    __tablename__ = "wearable_anomalies"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    patient_id: uuid.UUID = Field(foreign_key="patients.id")
    metric: str = Field(max_length=50)
    anomaly_type: str = Field(max_length=30)  # point_anomaly, trend_anomaly, threshold_breach
    detected_at: datetime = Field(sa_column=Column(TIMESTAMP(timezone=True), nullable=False))
    value: float
    baseline_mean: float
    z_score: float | None = None
    trend_slope: float | None = None
    trend_window: int | None = None
    severity: str = Field(max_length=10)  # low, medium, high
    resolved: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )
