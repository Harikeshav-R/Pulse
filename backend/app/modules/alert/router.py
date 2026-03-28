"""Alert management API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from app.deps import get_db, get_current_staff
from app.modules.alert.service import get_alerts, update_alert

logger = logging.getLogger(__name__)
router = APIRouter(tags=["alerts"])


class AlertUpdateRequest(SQLModel):
    action: str  # acknowledge, resolve, dismiss, escalate
    note: str | None = None


@router.get("/dashboard/alerts")
async def list_alerts(
    trial_id: str = Query(...),
    status: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    staff: dict = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    """Get alerts for a trial with optional status/severity filters."""
    return await get_alerts(trial_id, status, severity, db)


@router.put("/dashboard/alerts/{alert_id}")
async def update_alert_endpoint(
    alert_id: str,
    body: AlertUpdateRequest,
    staff: dict = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    """Update an alert's status (acknowledge, resolve, dismiss, escalate)."""
    try:
        return await update_alert(
            alert_id=alert_id,
            action=body.action,
            note=body.note,
            staff_id=staff["staff_id"],
            db=db,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
