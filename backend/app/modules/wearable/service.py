"""Wearable data service — ingestion, anomaly detection, and summaries."""

import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wearable import WearableReading, WearableBaseline, WearableAnomaly
from app.modules.wearable.normalization import normalize_reading
from app.modules.wearable.anomaly_detection import detect_point_anomaly, detect_trend_anomaly

logger = logging.getLogger(__name__)


async def sync_readings(
    patient_id: str,
    readings: list[dict],
    db: AsyncSession,
    event_bus=None,
) -> dict:
    """Ingest and normalize wearable readings, then trigger anomaly checks."""
    logger.info("Syncing %d readings for patient %s", len(readings), patient_id)
    pid = uuid.UUID(patient_id)
    accepted = 0

    for r in readings:
        normalized = normalize_reading(r["metric"], r["value"])
        if normalized is None:
            continue

        reading = WearableReading(
            patient_id=pid,
            metric=r["metric"],
            value=normalized,
            source=r.get("source"),
            quality=r.get("quality", "raw"),
            recorded_at=datetime.fromisoformat(r["recorded_at"]),
        )
        db.add(reading)
        accepted += 1

    await db.flush()

    if event_bus:
        await event_bus.publish("wearable.data_received", {
            "patient_id": patient_id,
            "readings_count": accepted,
        })

    logger.info("Accepted %d/%d readings for patient %s", accepted, len(readings), patient_id)
    return {"accepted": accepted, "rejected": len(readings) - accepted}


async def handle_wearable_data_received(payload: dict) -> None:
    """Event handler: run anomaly detection on newly received wearable data."""
    from app.main import async_session_factory, event_bus

    patient_id = payload["patient_id"]
    logger.info("Running anomaly detection for patient %s", patient_id)

    async with async_session_factory() as db:
        pid = uuid.UUID(patient_id)

        # Get current baselines
        baselines_result = await db.execute(
            select(WearableBaseline)
            .where(WearableBaseline.patient_id == pid, WearableBaseline.is_current == True)
        )
        baselines = {b.metric: b for b in baselines_result.scalars().all()}

        for metric, baseline in baselines.items():
            # Get latest reading
            latest_result = await db.execute(
                select(WearableReading)
                .where(WearableReading.patient_id == pid, WearableReading.metric == metric)
                .order_by(WearableReading.recorded_at.desc())
                .limit(1)
            )
            latest = latest_result.scalars().first()
            if not latest:
                continue

            # Point anomaly detection
            anomaly = detect_point_anomaly(
                latest.value,
                baseline.baseline_mean,
                baseline.baseline_stddev,
            )
            if anomaly:
                anomaly_record = WearableAnomaly(
                    patient_id=pid,
                    metric=metric,
                    anomaly_type="point_anomaly",
                    detected_at=datetime.now(timezone.utc),
                    value=latest.value,
                    baseline_mean=baseline.baseline_mean,
                    z_score=anomaly["z_score"],
                    severity=anomaly["severity"],
                )
                db.add(anomaly_record)
                await db.flush()

                await event_bus.publish("anomaly.detected", {
                    "patient_id": patient_id,
                    "anomaly_id": str(anomaly_record.id),
                    "metric": metric,
                    "anomaly_type": "point_anomaly",
                    "value": latest.value,
                    "baseline_mean": baseline.baseline_mean,
                    "z_score": anomaly["z_score"],
                    "severity": anomaly["severity"],
                })

            # Trend anomaly detection (last 7 daily averages)
            seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
            daily_result = await db.execute(
                select(
                    func.date_trunc("day", WearableReading.recorded_at).label("day"),
                    func.avg(WearableReading.value).label("avg_val"),
                )
                .where(
                    WearableReading.patient_id == pid,
                    WearableReading.metric == metric,
                    WearableReading.recorded_at >= seven_days_ago,
                )
                .group_by("day")
                .order_by("day")
            )
            daily_rows = daily_result.all()
            if len(daily_rows) >= 5:
                daily_values = [float(row.avg_val) for row in daily_rows]
                trend = detect_trend_anomaly(daily_values, window_days=len(daily_values))
                if trend:
                    trend_record = WearableAnomaly(
                        patient_id=pid,
                        metric=metric,
                        anomaly_type="trend_anomaly",
                        detected_at=datetime.now(timezone.utc),
                        value=daily_values[-1],
                        baseline_mean=baseline.baseline_mean,
                        trend_slope=trend["trend_slope"],
                        trend_window=trend["trend_window"],
                        severity=trend["severity"],
                    )
                    db.add(trend_record)
                    await db.flush()

                    await event_bus.publish("anomaly.detected", {
                        "patient_id": patient_id,
                        "anomaly_id": str(trend_record.id),
                        "metric": metric,
                        "anomaly_type": "trend_anomaly",
                        "value": daily_values[-1],
                        "baseline_mean": baseline.baseline_mean,
                        "trend_slope": trend["trend_slope"],
                        "severity": trend["severity"],
                    })

        await db.commit()
    logger.info("Anomaly detection complete for patient %s", patient_id)


async def get_wearable_summary(
    patient_id: str,
    days: int,
    db: AsyncSession,
) -> dict:
    """Get aggregated wearable metrics summary for a patient."""
    pid = uuid.UUID(patient_id)
    since = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(
            WearableReading.metric,
            func.avg(WearableReading.value).label("avg_val"),
            func.min(WearableReading.value).label("min_val"),
            func.max(WearableReading.value).label("max_val"),
            func.count(WearableReading.id).label("reading_count"),
        )
        .where(WearableReading.patient_id == pid, WearableReading.recorded_at >= since)
        .group_by(WearableReading.metric)
    )

    metrics = {}
    for row in result.all():
        metrics[row.metric] = {
            "avg": round(float(row.avg_val), 1),
            "min": float(row.min_val),
            "max": float(row.max_val),
            "readings": row.reading_count,
        }

    return {"patient_id": patient_id, "days": days, "metrics": metrics}
