import pytest
import uuid
from unittest.mock import MagicMock

from app.modules.alert.risk_scoring import _score_tier

def test_score_tier_mapping():
    assert _score_tier(0) == "low"
    assert _score_tier(29) == "low"
    assert _score_tier(30) == "low"
    assert _score_tier(31) == "medium"
    assert _score_tier(59) == "medium"
    assert _score_tier(60) == "medium"
    assert _score_tier(61) == "high"
    assert _score_tier(100) == "high"

@pytest.mark.asyncio
async def test_calculate_risk_score_with_high_symptoms(mock_db_session):
    from app.modules.alert.risk_scoring import calculate_risk_score
    from app.models.symptom import SymptomEntry
    
    # Mocking symptom queries
    mock_symptom1 = MagicMock(spec=SymptomEntry)
    mock_symptom1.severity_grade = 3
    mock_symptom1.meddra_pt_term = "Nausea"
    
    mock_symptom2 = MagicMock(spec=SymptomEntry)
    mock_symptom2.severity_grade = 4
    mock_symptom2.meddra_pt_term = "Fatigue"
    
    
    class MockResult:
        def __init__(self, items):
            self.items = items
            
        def scalars(self):
            class Scalars:
                def all(self_inner):
                    return self.items
                def first(self_inner):
                    return self.items[0] if self.items else None
            return Scalars()
            
        def scalar(self):
            return self.items[0] if self.items else None

    # We need to route the mock_db_session.execute based on the query,
    # or just return an ordered sequence of results for the 5 executions.
    # The executions are:
    # 1. symptoms_result (all)
    # 2. sessions_result (last 2 sessions) (all)
    # 3. anomalies_result (all)
    # 4. last_active_result (first)
    # 5. total_sessions count (scalar)
    # 6. completed_sessions count (scalar)
    
    mock_db_session.execute.side_effect = [
        MockResult([mock_symptom1, mock_symptom2]), # symptoms: two severe
        MockResult([]), # sessions worsening
        MockResult([]), # anomalies
        MockResult([]), # last active
        MockResult([10]), # total checkins
        MockResult([10]), # completed checkins
    ]
    
    pid = str(uuid.uuid4())
    result = await calculate_risk_score(pid, mock_db_session)
    
    assert result["patient_id"] == pid
    assert result["components"]["symptom"] == 30  # 15 + 15
    assert "Grade 3 Nausea" in result["factors"]
