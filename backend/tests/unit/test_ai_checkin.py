import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_langchain_agent():
    with patch("app.ai.graphs.checkin_graph.create_agent") as mock_create:
        mock_agent = AsyncMock()
        mock_create.return_value = mock_agent
        yield mock_agent

@pytest.mark.asyncio
async def test_checkin_greeting_node_transitions_to_screening(mock_langchain_agent):
    from app.ai.graphs.checkin_graph import conversation_node
    
    # Mock the response tool call logic: pretend the user selected overall feeling.
    # We will simulate the AI sending a message of type 'tool' with 'overall_feeling'
    class MockMessage:
        def __init__(self, msg_type, content):
            self.type = msg_type
            self.content = content
            
    mock_msg = MockMessage("tool", '{"type": "overall_feeling", "rating": 4}')
    mock_langchain_agent.ainvoke.return_value = {"messages": [mock_msg]}
    
    state = {
        "messages": [],
        "phase": "greeting",
        "overall_feeling": None,
        "reported_symptoms": [],
        "protocol_context": {},
        "session_complete": False,
        "ai_response": ""
    }
    
    result = await conversation_node(state)
    
    assert result["phase"] == "symptom_screening"
    assert result["overall_feeling"] == 4

def test_should_continue_router():
    from app.ai.graphs.checkin_graph import should_continue
    
    state_complete = {"session_complete": True}
    assert should_continue(state_complete) == "__end__"
    
    state_incomplete = {"session_complete": False}
    assert should_continue(state_incomplete) == "conversation"

@pytest.mark.asyncio
async def test_classifier_validation_node():
    from app.ai.graphs.classifier_graph import validate_node
    from app.ai.schemas import ClassificationResult, SymptomClassification
    
    symptoms = [
        SymptomClassification(meddra_pt_term="Nausea", severity_ctcae=3, confidence=0.95, meddra_pt_code="10028813", meddra_soc="Gastro", symptom_text="Bad nausea"),
        SymptomClassification(meddra_pt_term="FakeSymptom", severity_ctcae=5, confidence=0.2, meddra_pt_code="000", meddra_soc="None", symptom_text="Tired"), # low conf, invalid severity
    ]
    
    classification = ClassificationResult(symptoms=symptoms, total_symptoms=2, has_severe_symptoms=True)
    
    state = {
        "conversation_text": "I feel nausea and tired",
        "protocol_context": {},
        "classification": classification,
        "is_validated": False
    }
    
    result = await validate_node(state)
    assert result["is_validated"] is True
    validated_cls = result["classification"]
    assert validated_cls.total_symptoms == 1
    assert validated_cls.symptoms[0].meddra_pt_term == "Nausea"
