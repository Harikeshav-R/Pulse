"""LangGraph classifier pipeline — extracts and classifies symptoms.

Uses create_agent with structured output (ToolStrategy) inside a
LangGraph StateGraph for the extract → validate pipeline.
"""

import logging

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain.tools import tool
from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict

from app.ai.prompts.classifier_system import CLASSIFIER_SYSTEM_PROMPT
from app.ai.schemas import ClassificationResult
from app.ai.tools.meddra_lookup import lookup_by_code
from app.config import settings

logger = logging.getLogger(__name__)


# ─── State ───


class ClassifierState(TypedDict):
    """State for the classification pipeline."""

    conversation_text: str
    protocol_context: dict
    classification: ClassificationResult | None
    is_validated: bool


# ─── Tools ───


@tool
def validate_meddra_code(code: str) -> str:
    """Validate a MedDRA code against the known lookup table.

    Args:
        code: MedDRA PT code to validate (e.g., '10028813')
    """
    result = lookup_by_code(code)
    if result:
        return f"Valid: {result['pt_term']} ({result['soc']})"
    return f"Code {code} not found in local MedDRA table. Use your best judgment for the mapping."


# ─── Nodes ───


async def extract_node(state: ClassifierState) -> dict:
    """Extract and classify symptoms using create_agent with structured output."""
    logger.info("Classifier: extracting symptoms from conversation")

    ctx = state.get("protocol_context", {})
    system_prompt = CLASSIFIER_SYSTEM_PROMPT.format(
        expected_side_effects=str(ctx.get("expected_side_effects", [])),
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

    result = await agent.ainvoke({
        "messages": [
            {"role": "user", "content": f"Classify symptoms:\n\n{state['conversation_text']}"}
        ],
    })

    classification: ClassificationResult | None = result.get("structured_response")
    logger.info(
        "Classifier: extracted %d symptoms",
        classification.total_symptoms if classification else 0,
    )
    return {"classification": classification}


async def validate_node(state: ClassifierState) -> dict:
    """Validate classification results — filter low-confidence entries."""
    classification = state.get("classification")
    if not classification:
        logger.warning("Classifier: no classification to validate")
        return {"is_validated": True}

    valid_symptoms = [
        s for s in classification.symptoms
        if s.confidence > 0.5 and 1 <= s.severity_ctcae <= 5
    ]
    rejected = len(classification.symptoms) - len(valid_symptoms)

    if rejected > 0:
        logger.warning("Classifier: rejected %d low-confidence classifications", rejected)

    validated = ClassificationResult(
        symptoms=valid_symptoms,
        total_symptoms=len(valid_symptoms),
        has_severe_symptoms=any(s.severity_ctcae >= 3 for s in valid_symptoms),
    )

    logger.info(
        "Classifier: validated %d symptoms (severe=%s)",
        validated.total_symptoms,
        validated.has_severe_symptoms,
    )
    return {"classification": validated, "is_validated": True}


# ─── Graph builder ───


def build_classifier_graph():
    """Build the classifier LangGraph pipeline: extract → validate."""
    graph = StateGraph(ClassifierState)

    graph.add_node("extract", extract_node)
    graph.add_node("validate", validate_node)

    graph.set_entry_point("extract")
    graph.add_edge("extract", "validate")
    graph.add_edge("validate", END)

    compiled = graph.compile()
    logger.info("Classifier LangGraph compiled")
    return compiled
