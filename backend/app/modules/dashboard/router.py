"""Dashboard API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_current_staff
from app.modules.dashboard.service import (
    get_trial_overview,
    get_patient_detail,
    get_patient_list,
    review_symptom,
    get_patient_wearable_summary,
    get_patient_timeline,
)
from app.schemas.dashboard import (
    PatientListResponse,
    PatientWearableDataResponse,
    PatientTimelineResponse,
)
from app.schemas.symptom import SymptomReviewRequest, SymptomReviewResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/trial/{trial_id}/overview")
async def trial_overview(
    trial_id: str,
    staff: dict = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    """Get high-level trial overview with alert and risk summaries."""
    return await get_trial_overview(trial_id, db)


@router.get("/dashboard/patients/{patient_id}")
async def patient_detail(
    patient_id: str,
    staff: dict = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed patient view with symptoms, alerts, and risk score."""
    try:
        return await get_patient_detail(patient_id, db)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/dashboard/patients", response_model=PatientListResponse)
async def list_patients(
    trial_id: str = Query(...),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    staff: dict = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    """List and paginate patients for a given trial."""
    return await get_patient_list(trial_id, limit, offset, db)


@router.post("/dashboard/symptoms/{symptom_id}/review", response_model=SymptomReviewResponse)
async def review_symptom_endpoint(
    symptom_id: str,
    request: SymptomReviewRequest,
    staff: dict = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    """CRC (Staff) confirms or overrides an AI-classified symptom."""
    try:
        return await review_symptom(symptom_id, request, staff["staff_id"], db)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/dashboard/patients/{patient_id}/wearable", response_model=PatientWearableDataResponse)
async def patient_wearable_summary(
    patient_id: str,
    metric: str = Query("heart_rate"),
    days: int = Query(7, ge=1, le=30),
    staff: dict = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated wearable data for a given metric and timeframe."""
    return await get_patient_wearable_summary(patient_id, metric, days, db)


@router.get("/dashboard/patients/{patient_id}/timeline", response_model=PatientTimelineResponse)
async def patient_timeline(
    patient_id: str,
    staff: dict = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    """Return a unified chronological list of patient events."""
    return await get_patient_timeline(patient_id, db)
