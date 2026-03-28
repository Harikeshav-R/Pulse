"""Wearable API endpoints."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db, get_current_patient, get_event_bus
from app.modules.wearable.service import sync_readings, get_wearable_summary
from app.schemas.wearable import WearableSyncRequest, WearableSyncResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["wearable"])


@router.post("/wearable/sync", response_model=WearableSyncResponse)
async def sync_wearable_endpoint(
    body: WearableSyncRequest,
    patient: dict = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
    event_bus=Depends(get_event_bus),
):
    """Sync wearable readings from the patient's device."""
    return await sync_readings(
        patient_id=patient["patient_id"],
        readings=[r.model_dump() for r in body.readings],
        db=db,
        event_bus=event_bus,
    )


@router.get("/wearable/summary")
async def get_summary_endpoint(
    days: int = 7,
    patient: dict = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated wearable summary for the current patient."""
    return await get_wearable_summary(patient["patient_id"], days, db)
