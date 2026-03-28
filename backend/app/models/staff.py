"""Staff and site access models."""

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel, Column
from sqlalchemy import TIMESTAMP


class Staff(SQLModel, table=True):
    __tablename__ = "staff"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True)
    password_hash: str = Field(max_length=255)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    role: str = Field(max_length=30)  # crc, pi, medical_monitor, study_manager
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )


class StaffSiteAccess(SQLModel, table=True):
    __tablename__ = "staff_site_access"

    staff_id: uuid.UUID = Field(foreign_key="staff.id", primary_key=True)
    site_id: uuid.UUID = Field(foreign_key="sites.id", primary_key=True)
    role: str = Field(max_length=30)
