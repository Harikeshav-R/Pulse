import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_current_patient
from app.modules.patient.service import (
    get_patient_profile,
    get_checkin_history,
    get_symptom_history,
)
from app.schemas.patient import PatientProfileResponse
from app.schemas.checkin import CheckinHistoryResponse
from app.schemas.symptom import SymptomHistoryResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["patient"])


@router.get("/patient/profile", response_model=PatientProfileResponse)
async def patient_profile(
    patient: dict = Depends(get_current_patient), db: AsyncSession = Depends(get_db)
):
    try:
        return await get_patient_profile(patient["patient_id"], db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/checkins/history", response_model=CheckinHistoryResponse)
async def checkin_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    patient: dict = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
):
    return await get_checkin_history(patient["patient_id"], limit, offset, db)


@router.get("/symptoms/history", response_model=SymptomHistoryResponse)
async def symptom_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    patient: dict = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
):
    return await get_symptom_history(patient["patient_id"], limit, offset, db)
