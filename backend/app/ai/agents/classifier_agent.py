"""LangChain v1 agent for symptom classification with structured output.

Uses create_agent with ToolStrategy(ClassificationResult) to return
validated Pydantic models instead of raw JSON.
"""

import logging

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain.tools import tool

from app.ai.prompts.classifier_system import CLASSIFIER_SYSTEM_PROMPT
from app.ai.schemas import ClassificationResult, SymptomClassification
from app.ai.tools.meddra_lookup import lookup_by_code
from app.config import settings

logger = logging.getLogger(__name__)


@tool
def validate_meddra_code(code: str) -> str:
    """Validate a MedDRA code against the known lookup table.

    Args:
        code: MedDRA PT code to validate (e.g., '10028813')

    Returns:
        The validated term info or a message if not found.
    """
    result = lookup_by_code(code)
    if result:
        return f"Valid: {result['pt_term']} ({result['soc']})"
    return f"Code {code} not found in MedDRA lookup table. Use your best judgment."


def create_classifier_agent(protocol_context: dict):
    """Create a symptom classification agent with structured output.

    The agent analyzes conversation transcripts and returns a validated
    ClassificationResult Pydantic model containing all classified symptoms.
    """
    system_prompt = CLASSIFIER_SYSTEM_PROMPT.format(
        expected_side_effects=str(protocol_context.get("expected_side_effects", [])),
    )

    agent = create_agent(
        model=settings.LLM_MODEL,
        tools=[validate_meddra_code],
        system_prompt=system_prompt,
        response_format=ToolStrategy(
            ClassificationResult,
            handle_errors=True,
        ),
    )

    logger.info("Classifier agent created with structured output (ClassificationResult)")
    return agent
