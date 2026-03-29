"""LangChain v1 agent-based check-in conversation.

Uses create_agent with tools for structured symptom collection,
replacing the old chain-based approach.
"""

import json
import logging

from langchain.agents import create_agent
from langchain.tools import tool

from app.ai.prompts.checkin_system import CHECKIN_SYSTEM_PROMPT
from app.ai.tools.meddra_lookup import lookup_by_term
from app.config import settings
from app.ai.llm import get_chat_model

logger = logging.getLogger(__name__)


# ─── Tools available to the check-in agent ───


@tool
def record_overall_feeling(rating: int) -> str:
    """Record the patient's overall feeling on a 1-5 scale.

    Args:
        rating: Patient's self-reported feeling (1=terrible, 5=great)
    """
    if not 1 <= rating <= 5:
        return "Rating must be between 1 and 5. Please ask again."
    return json.dumps({"recorded": True, "rating": rating})


@tool
def record_symptom(
    symptom_name: str,
    severity_1_to_10: int,
    description: str,
    onset: str = "",
    is_ongoing: bool = True,
) -> str:
    """Record a symptom reported by the patient during check-in.

    Args:
        symptom_name: Name of the symptom (e.g., 'headache', 'nausea')
        severity_1_to_10: Patient-reported severity on a 1-10 scale
        description: Patient's description in their own words
        onset: When the symptom started (e.g., 'yesterday', '3 days ago')
        is_ongoing: Whether the symptom is still present
    """
    meddra = lookup_by_term(symptom_name)
    result = {
        "recorded": True,
        "symptom": symptom_name,
        "severity": severity_1_to_10,
        "description": description,
        "onset": onset,
        "is_ongoing": is_ongoing,
        "meddra_match": meddra,
    }
    logger.info("Symptom recorded via tool: %s (severity: %d)", symptom_name, severity_1_to_10)
    return json.dumps(result)


@tool
def complete_checkin(summary: str) -> str:
    """Signal that the check-in conversation is complete.

    Call this when all symptoms have been discussed and the patient
    has confirmed the summary. This marks the session as done.

    Args:
        summary: Brief summary of everything reported in this check-in
    """
    return json.dumps({"session_complete": True, "summary": summary})


CHECKIN_TOOLS = [record_overall_feeling, record_symptom, complete_checkin]


def create_checkin_agent(protocol_context: dict):
    """Create a check-in conversation agent using LangChain v1 create_agent.

    The agent uses tools to structured-capture patient symptoms and feelings
    while maintaining a natural conversational flow.
    """
    system_prompt = CHECKIN_SYSTEM_PROMPT.format(
        therapeutic_area=protocol_context.get("therapeutic_area", "clinical"),
        protocol_number=protocol_context.get("protocol_number", ""),
        expected_side_effects=str(protocol_context.get("expected_side_effects", [])),
        phase="check-in",
    )

    agent = create_agent(
        model=get_chat_model(),
        tools=CHECKIN_TOOLS,
        system_prompt=system_prompt,
    )

    logger.info(
        "Check-in agent created for protocol %s",
        protocol_context.get("protocol_number", "unknown"),
    )
    return agent
