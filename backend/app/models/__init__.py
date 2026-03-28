"""SQLModel base and model registry.

All models are imported here so Alembic and the async engine
can discover them for table creation and migrations.
"""

from sqlmodel import SQLModel

# Import all models so they register with SQLModel.metadata
from app.models.trial import Trial, ProtocolConfig, Site  # noqa: F401
from app.models.staff import Staff, StaffSiteAccess  # noqa: F401
from app.models.patient import Patient, PatientAppAccount  # noqa: F401
from app.models.checkin import CheckinSession, CheckinMessage  # noqa: F401
from app.models.symptom import SymptomEntry  # noqa: F401
from app.models.wearable import (  # noqa: F401
    WearableConnection,
    WearableReading,
    WearableBaseline,
    WearableAnomaly,
)
from app.models.alert import Alert, RiskScore  # noqa: F401

__all__ = [
    "SQLModel",
    "Trial",
    "ProtocolConfig",
    "Site",
    "Staff",
    "StaffSiteAccess",
    "Patient",
    "PatientAppAccount",
    "CheckinSession",
    "CheckinMessage",
    "SymptomEntry",
    "WearableConnection",
    "WearableReading",
    "WearableBaseline",
    "WearableAnomaly",
    "Alert",
    "RiskScore",
]
