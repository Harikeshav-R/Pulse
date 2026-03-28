"""Seed realistic check-in data and symptoms for a demo patient."""

import asyncio
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.main import async_session_factory
from app.models.patient import Patient
from app.models.checkin import CheckinSession, CheckinMessage
from app.models.symptom import SymptomEntry
from app.models.wearable import WearableBaseline


async def seed_data():
    async with async_session_factory() as db:
        # Pick the first enrolled patient
        patient = (
            (await db.execute(select(Patient).where(Patient.status == "enrolled").limit(1)))
            .scalars()
            .first()
        )
        if not patient:
            print("No enrolled patient found. Please run db/seed.sql first.")
            return

        print(f"Seeding demo data for patient: {patient.subject_id} ({patient.id})")

        # Ensure WearableBaseline exists
        baseline = (
            (
                await db.execute(
                    select(WearableBaseline).where(
                        WearableBaseline.patient_id == patient.id,
                        WearableBaseline.metric == "heart_rate",
                    )
                )
            )
            .scalars()
            .first()
        )
        if not baseline:
            db.add(
                WearableBaseline(
                    patient_id=patient.id,
                    metric="heart_rate",
                    baseline_mean=72.5,
                    baseline_stddev=4.2,
                    baseline_min=60.0,
                    baseline_max=105.0,
                    sample_count=14,
                    baseline_start=datetime.now(timezone.utc).date() - timedelta(days=21),
                    baseline_end=datetime.now(timezone.utc).date() - timedelta(days=7),
                )
            )
            await db.flush()

        # Generate past check-ins (1-5 days ago)
        now = datetime.now(timezone.utc)
        for i in range(1, 6):
            checkin_time = now - timedelta(days=6 - i)
            # Make the checkin completed
            session = CheckinSession(
                patient_id=patient.id,
                session_type="scheduled",
                modality="text",
                status="completed",
                started_at=checkin_time,
                completed_at=checkin_time + timedelta(minutes=random.randint(2, 5)),
                duration_seconds=random.randint(120, 300),
                overall_feeling=random.randint(3, 5),
            )
            db.add(session)
            await db.flush()

            # Add some transcript messages
            db.add(
                CheckinMessage(
                    session_id=session.id,
                    sequence_number=1,
                    role="ai",
                    content="Hello, how are you feeling today?",
                )
            )
            db.add(
                CheckinMessage(
                    session_id=session.id,
                    sequence_number=2,
                    role="patient",
                    content="I'm feeling okay, a bit tired.",
                )
            )
            db.add(
                CheckinMessage(
                    session_id=session.id,
                    sequence_number=3,
                    role="ai",
                    content="Are you experiencing any specific symptoms like headache or fever?",
                )
            )

            if i == 5:  # The most recent one has a symptom
                db.add(
                    CheckinMessage(
                        session_id=session.id,
                        sequence_number=4,
                        role="patient",
                        content="Yes, I have a slight headache.",
                    )
                )
                symptom = SymptomEntry(
                    patient_id=patient.id,
                    session_id=session.id,
                    symptom_text="slight headache",
                    meddra_pt_term="Headache",
                    severity_grade=1,
                    is_ongoing=True,
                    ai_confidence=0.92,
                    created_at=checkin_time,
                )
                db.add(symptom)
            else:
                db.add(
                    CheckinMessage(
                        session_id=session.id,
                        sequence_number=4,
                        role="patient",
                        content="No, nothing else.",
                    )
                )

        await db.commit()
        print("Demo check-in data seeded successfully.")


if __name__ == "__main__":
    asyncio.run(seed_data())
