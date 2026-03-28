"""Wearable data normalization rules per TECHNICAL_DOC §6.3."""

import logging

logger = logging.getLogger(__name__)

NORMALIZATION_RULES: dict[str, dict] = {
    "heart_rate": {"min": 30, "max": 250, "precision": 0, "unit": "bpm"},
    "resting_heart_rate": {"min": 30, "max": 200, "precision": 0, "unit": "bpm"},
    "steps": {"min": 0, "max": 100000, "precision": 0, "unit": "steps"},
    "sleep_minutes": {"min": 0, "max": 1440, "precision": 0, "unit": "minutes"},
    "spo2": {"min": 50, "max": 100, "precision": 1, "unit": "%"},
}


def normalize_reading(metric: str, value: float) -> float | None:
    """Validate and normalize a wearable reading.

    Returns the normalized value, or None if the value is out of range.
    """
    rules = NORMALIZATION_RULES.get(metric)
    if not rules:
        logger.warning("Unknown wearable metric: %s", metric)
        return value

    if value < rules["min"] or value > rules["max"]:
        logger.warning(
            "Wearable reading out of range: metric=%s, value=%s (range: %s-%s)",
            metric,
            value,
            rules["min"],
            rules["max"],
        )
        return None

    return round(value, rules["precision"])
