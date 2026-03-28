"""Authentication API endpoints — demo login for hackathon."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from app.deps import get_db
from app.modules.auth.service import patient_demo_login, staff_demo_login

logger = logging.getLogger(__name__)
router = APIRouter(tags=["auth"])


# ─── Request/Response schemas ───


class PatientDemoLoginRequest(SQLModel):
    patient_id: str


class PatientDemoLoginResponse(SQLModel):
    patient_id: str
    subject_id: str
    access_token: str


class StaffDemoLoginRequest(SQLModel):
    staff_id: str


class StaffDemoLoginResponse(SQLModel):
    access_token: str
    staff: dict


# ─── Endpoints ───


@router.post("/auth/patient/demo-login", response_model=PatientDemoLoginResponse)
async def patient_login(body: PatientDemoLoginRequest, db: AsyncSession = Depends(get_db)):
    """Demo login for patients — issue JWT without password verification."""
    try:
        result = await patient_demo_login(body.patient_id, db)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/auth/staff/demo-login", response_model=StaffDemoLoginResponse)
async def staff_login(body: StaffDemoLoginRequest, db: AsyncSession = Depends(get_db)):
    """Demo login for staff — issue JWT without password verification."""
    try:
        result = await staff_demo_login(body.staff_id, db)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
