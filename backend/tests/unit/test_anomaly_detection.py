import pytest
import uuid
from unittest.mock import MagicMock

from app.modules.wearable.anomaly_detection import (
    detect_point_anomaly,
    detect_trend_anomaly,
    calculate_baseline,
    evaluate_contextual_suppression,
)


def test_detect_point_anomaly_fires_high_severity():
    result = detect_point_anomaly(
        value=110.0,
        baseline_mean=70.0,
        baseline_stddev=5.0,
        z_threshold=2.5,
    )
    assert result is not None
    assert result["anomaly_type"] == "point_anomaly"
    assert result["severity"] == "high"


def test_detect_point_anomaly_ignores_normal_variance():
    result = detect_point_anomaly(
        value=75.0,
        baseline_mean=70.0,
        baseline_stddev=5.0,
        z_threshold=2.5,
    )
    assert result is None


def test_detect_trend_anomaly_fires_on_steady_increase():
    daily_values = [70, 72, 74, 76, 78, 80, 82]
    result = detect_trend_anomaly(
        daily_values=daily_values,
        window_days=7,
        min_slope_per_day=1.5,
    )
    assert result is not None
    assert result["trend_slope"] >= 1.5
    assert result["severity"] in ("medium", "high")


def test_detect_trend_anomaly_ignores_noise():
    daily_values = [70, 75, 72, 76, 71, 74, 70]
    result = detect_trend_anomaly(
        daily_values=daily_values,
        window_days=7,
        min_slope_per_day=1.5,
    )
    assert result is None


def test_calculate_baseline():
    values = [60.0, 62.0, 58.0, 61.0, 59.0]
    baseline = calculate_baseline(values)
    assert baseline["sample_count"] == 5
    assert baseline["baseline_min"] == 58.0
    assert baseline["baseline_max"] == 62.0


@pytest.mark.asyncio
async def test_contextual_suppression_with_fever(mock_db_session):
    mock_fever_record = MagicMock()
    mock_fever_record.meddra_pt_term = "Pyrexia"
    
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = mock_fever_record
    
    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value = mock_scalars
    
    mock_db_session.execute.return_value = mock_execute_result
    
    patient_id = uuid.uuid4()
    suppressed, new_severity = await evaluate_contextual_suppression(
        patient_id=patient_id, 
        metric="heart_rate", 
        anomaly_severity="high", 
        db=mock_db_session
    )
    
    assert suppressed is False
    assert new_severity == "low"
