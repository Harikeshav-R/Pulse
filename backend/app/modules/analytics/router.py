"""Analytics API endpoints."""

import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_current_staff
from app.modules.analytics.service import (
    get_symptom_trends,
    get_risk_score_history,
    get_checkin_compliance,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["analytics"])


@router.get("/analytics/symptom-trends")
async def symptom_trends(
    trial_id: str = Query(...),
    days: int = Query(default=30),
    staff: dict = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    """Get daily symptom counts grouped by MedDRA term."""
    return await get_symptom_trends(trial_id, days, db)


@router.get("/analytics/risk-history/{patient_id}")
async def risk_history(
    patient_id: str,
    days: int = Query(default=30),
    staff: dict = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    """Get risk score history for a patient."""
    return await get_risk_score_history(patient_id, days, db)


@router.get("/analytics/checkin-compliance")
async def checkin_compliance(
    trial_id: str = Query(...),
    days: int = Query(default=30),
    staff: dict = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    """Get check-in compliance statistics across the trial."""
    return await get_checkin_compliance(trial_id, days, db)
