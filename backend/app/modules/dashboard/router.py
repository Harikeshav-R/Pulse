"""Dashboard API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_current_staff
from app.modules.dashboard.service import get_trial_overview, get_patient_detail

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
