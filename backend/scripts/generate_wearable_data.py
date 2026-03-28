"""Generate realistic wearable data over the last 14 days and test anomaly."""

import asyncio
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.main import async_session_factory
from app.models.patient import Patient
from app.modules.wearable.service import sync_readings


# Mock event bus
class MockEventBus:
    async def publish(self, topic: str, payload: dict):
        print(f"[EventBus] {topic}: {payload}")


async def generate_data(anomaly: bool = False):
    async with async_session_factory() as db:
        patient = (
            (await db.execute(select(Patient).where(Patient.status == "enrolled").limit(1)))
            .scalars()
            .first()
        )
        if not patient:
            print("No enrolled patient found.")
            return

        print(f"Generating wearable data for patient: {patient.subject_id} ({patient.id})")
        now = datetime.now(timezone.utc)
        readings = []

        # 14 days of data, 1 reading per hour
        for day in range(14, 0, -1):
            for hour in range(24):
                record_time = now - timedelta(days=day, hours=hour)
                # Baseline 72 +- 5
                val = random.gauss(72, 4)
                if hour < 7:  # Sleep
                    val -= 10
                elif 17 <= hour <= 19:  # Exercise/active
                    val += 20
                readings.append(
                    {
                        "metric": "heart_rate",
                        "value": val,
                        "recorded_at": record_time.isoformat(),
                        "source": "apple_health",
                        "quality": "hourly_avg",
                    }
                )

        # Add anomaly right now if requested
        if anomaly:
            readings.append(
                {
                    "metric": "heart_rate",
                    "value": 135.0,  # Spike!
                    "recorded_at": now.isoformat(),
                    "source": "apple_health",
                    "quality": "raw",
                }
            )

        print(f"Pushing {len(readings)} readings to service...")
        bus = MockEventBus()
        await sync_readings(str(patient.id), readings, db, event_bus=bus)
        await db.commit()
        print("Generation complete.")


if __name__ == "__main__":
    import sys

    do_anomaly = "--anomaly" in sys.argv
    asyncio.run(generate_data(do_anomaly))
