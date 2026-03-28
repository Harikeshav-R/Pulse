"""Anomaly detection algorithms per TECHNICAL_DOC §6.4.

Implements point anomaly detection (z-score), trend anomaly detection
(linear regression slope), and contextual suppression.
"""

import logging
import uuid
from datetime import datetime, timedelta, timezone

import numpy as np
from scipy import stats
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.symptom import SymptomEntry

logger = logging.getLogger(__name__)


def detect_point_anomaly(
    value: float,
    baseline_mean: float,
    baseline_stddev: float,
    z_threshold: float = 2.5,
) -> dict | None:
    """Detect point anomaly via z-score against the patient's baseline.

    Returns anomaly dict if z_score exceeds threshold, else None.
    """
    if baseline_stddev == 0:
        return None

    z_score = abs(value - baseline_mean) / baseline_stddev

    if z_score >= z_threshold:
        severity = "high" if z_score >= 3.5 else "medium"
        logger.info(
            "Point anomaly detected: value=%.1f, mean=%.1f, z=%.2f, severity=%s",
            value,
            baseline_mean,
            z_score,
            severity,
        )
        return {
            "anomaly_type": "point_anomaly",
            "value": value,
            "baseline_mean": baseline_mean,
            "z_score": round(z_score, 2),
            "severity": severity,
        }
    return None


def detect_trend_anomaly(
    daily_values: list[float],
    window_days: int = 7,
    min_slope_per_day: float = 1.5,
) -> dict | None:
    """Detect trend anomaly via linear regression over a time window.

    Fits a line to the last `window_days` daily values and checks if
    the slope exceeds the threshold.
    """
    if len(daily_values) < window_days:
        return None

    window = daily_values[-window_days:]
    x = np.arange(len(window))
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, window)

    if abs(slope) >= min_slope_per_day and p_value < 0.05:
        severity = "high" if abs(slope) >= min_slope_per_day * 2 else "medium"
        direction = "increasing" if slope > 0 else "decreasing"
        logger.info(
            "Trend anomaly detected: slope=%.2f/day (%s), r²=%.3f, p=%.4f",
            slope,
            direction,
            r_value**2,
            p_value,
        )
        return {
            "anomaly_type": "trend_anomaly",
            "value": window[-1],
            "trend_slope": round(slope, 2),
            "trend_window": window_days,
            "r_squared": round(r_value**2, 3),
            "p_value": round(p_value, 4),
            "severity": severity,
        }
    return None


def calculate_baseline(values: list[float]) -> dict:
    """Calculate baseline statistics from a list of readings.

    Uses the first 14 days of data to establish a patient-specific baseline.
    """
    arr = np.array(values)
    return {
        "baseline_mean": round(float(np.mean(arr)), 2),
        "baseline_stddev": round(float(np.std(arr, ddof=1)), 2),
        "baseline_min": round(float(np.min(arr)), 2),
        "baseline_max": round(float(np.max(arr)), 2),
        "sample_count": len(values),
    }


async def evaluate_contextual_suppression(
    patient_id: uuid.UUID, metric: str, anomaly_severity: str, db: AsyncSession
) -> tuple[bool, str]:
    """Check if an anomaly should be suppressed or downgraded due to recent symptoms.

    Returns (suppressed: bool, new_severity: str).
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=48)

    if metric == "heart_rate":
        recent_fever = (
            (
                await db.execute(
                    select(SymptomEntry)
                    .where(
                        SymptomEntry.patient_id == patient_id,
                        SymptomEntry.created_at >= cutoff,
                        SymptomEntry.meddra_pt_term.in_(["Pyrexia", "Fever"]),
                    )
                    .limit(1)
                )
            )
            .scalars()
            .first()
        )

        if recent_fever:
            logger.info(
                "Contextual suppression: Heart rate anomaly downgraded due to recent Pyrexia."
            )
            return False, "low"

    return False, anomaly_severity
