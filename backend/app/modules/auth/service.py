"""Authentication service — demo login for hackathon."""

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient import Patient
from app.models.staff import Staff, StaffSiteAccess
from app.models.trial import Site
from app.modules.auth.jwt import create_access_token

logger = logging.getLogger(__name__)


async def patient_demo_login(patient_id: str, db: AsyncSession) -> dict:
    """Demo login: look up patient and issue JWT with trial context.

    In production this would verify enrollment code + device attestation.
    For hackathon, we just issue a token for any valid patient_id.
    """
    result = await db.execute(
        select(Patient).where(Patient.id == uuid.UUID(patient_id))
    )
    patient = result.scalars().first()
    if not patient:
        raise ValueError(f"Patient not found: {patient_id}")

    # Get the trial_id through site
    site_result = await db.execute(select(Site).where(Site.id == patient.site_id))
    site = site_result.scalars().first()

    token = create_access_token({
        "sub": str(patient.id),
        "patient_id": str(patient.id),
        "site_id": str(patient.site_id),
        "trial_id": str(site.trial_id) if site else "",
        "subject_id": patient.subject_id,
        "role": "patient",
    })

    logger.info(
        "Patient demo login: patient_id=%s, subject_id=%s",
        patient_id,
        patient.subject_id,
    )
    return {
        "patient_id": str(patient.id),
        "subject_id": patient.subject_id,
        "access_token": token,
    }


async def staff_demo_login(staff_id: str, db: AsyncSession) -> dict:
    """Demo login: look up staff and issue JWT with site access info."""
    result = await db.execute(
        select(Staff).where(Staff.id == uuid.UUID(staff_id))
    )
    staff = result.scalars().first()
    if not staff:
        raise ValueError(f"Staff not found: {staff_id}")

    # Get sites this staff has access to
    access_result = await db.execute(
        select(StaffSiteAccess).where(StaffSiteAccess.staff_id == staff.id)
    )
    site_access = access_result.scalars().all()
    site_ids = [str(sa.site_id) for sa in site_access]

    token = create_access_token({
        "sub": str(staff.id),
        "staff_id": str(staff.id),
        "email": staff.email,
        "role": staff.role,
        "sites": site_ids,
    })

    logger.info(
        "Staff demo login: staff_id=%s, role=%s, sites=%d",
        staff_id,
        staff.role,
        len(site_ids),
    )
    return {
        "access_token": token,
        "staff": {
            "id": str(staff.id),
            "email": staff.email,
            "first_name": staff.first_name,
            "last_name": staff.last_name,
            "role": staff.role,
            "sites": site_ids,
        },
    }
