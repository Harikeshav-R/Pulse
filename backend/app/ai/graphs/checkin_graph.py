"""LangGraph check-in state machine.

Orchestrates the multi-step conversational check-in flow using LangGraph
StateGraph for orchestration. Each node uses LangChain v1 create_agent
for AI-powered interactions with tools.

Flow: greeting → overall_feeling → symptom_screening → [deep_dive] → summary → closing
"""

import json
import logging
from typing import Annotated, Literal

from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from app.ai.prompts.checkin_system import CHECKIN_SYSTEM_PROMPT
from app.ai.tools.meddra_lookup import lookup_by_term
from app.config import settings
from app.ai.llm import get_chat_model

logger = logging.getLogger(__name__)


# ─── State definition ───


class CheckinState(TypedDict):
    """State tracked across the check-in conversation."""

    messages: Annotated[list, add_messages]
    phase: str
    overall_feeling: int | None
    reported_symptoms: list
    protocol_context: dict
    session_complete: bool
    ai_response: str


# ─── Tools for the check-in agent ───


@tool
def record_overall_feeling(rating: int) -> str:
    """Record the patient's overall feeling on a 1-5 scale.

    Args:
        rating: Patient's self-reported feeling (1=terrible, 5=great)
    """
    if not 1 <= rating <= 5:
        return "Rating must be between 1 and 5. Please ask again."
    return json.dumps({"type": "overall_feeling", "rating": rating})


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
    return json.dumps({
        "type": "symptom",
        "symptom": symptom_name,
        "severity": severity_1_to_10,
        "description": description,
        "onset": onset,
        "is_ongoing": is_ongoing,
        "meddra_match": meddra,
    })


@tool
def mark_no_symptoms() -> str:
    """Mark that the patient has no new or worsening symptoms to report."""
    return json.dumps({"type": "no_symptoms"})


@tool
def complete_checkin(summary: str) -> str:
    """Signal that the check-in conversation is complete.

    Call this after summarizing all reported information and the patient confirms.

    Args:
        summary: Brief summary of everything reported in this check-in
    """
    return json.dumps({"type": "complete", "summary": summary})


CHECKIN_TOOLS = [record_overall_feeling, record_symptom, mark_no_symptoms, complete_checkin]


def _build_system_prompt(ctx: dict) -> str:
    """Format the system prompt with trial-specific context."""
    return CHECKIN_SYSTEM_PROMPT.format(
        therapeutic_area=ctx.get("therapeutic_area", "clinical"),
        protocol_number=ctx.get("protocol_number", ""),
        expected_side_effects=str(ctx.get("expected_side_effects", [])),
        phase="check-in",
    )


# ─── Graph nodes ───


async def conversation_node(state: CheckinState) -> dict:
    """Core conversation node — invokes the agent with the full message history.

    This node uses create_agent with tools to handle the natural conversation.
    The phase is embedded in the system prompt context so the agent knows
    where it is in the check-in flow.
    """
    ctx = state.get("protocol_context", {})
    phase = state.get("phase", "greeting")

    phase_instruction = {
        "greeting": "Greet the patient warmly and ask how they're feeling overall today.",
        "overall_feeling": "Ask the patient to rate how they feel on a 1-5 scale using the record_overall_feeling tool.",
        "symptom_screening": "Ask if they have any new or worsening symptoms. If they do, use record_symptom for each. If not, use mark_no_symptoms.",
        "deep_dive": f"The patient reported symptoms: {state.get('reported_symptoms', [])}. Ask detailed follow-up questions about severity, onset, duration, and impact on daily life for each symptom.",
        "summary": "Provide a brief summary of everything reported and ask if anything was missed.",
        "closing": "Thank the patient, remind them of their next check-in, and call complete_checkin with a summary.",
    }.get(phase, "Continue the conversation naturally.")

    system_prompt = _build_system_prompt(ctx) + f"\n\nCURRENT PHASE: {phase}\nINSTRUCTION: {phase_instruction}"

    agent = create_agent(
        model=get_chat_model(),
        tools=CHECKIN_TOOLS,
        system_prompt=system_prompt,
    )

    result = await agent.ainvoke({"messages": state["messages"]})

    # Extract AI response and tool call results
    result_messages = result.get("messages", [])
    ai_response = ""
    new_symptoms = list(state.get("reported_symptoms", []))
    overall = state.get("overall_feeling")
    complete = state.get("session_complete", False)
    next_phase = phase

    for m in result_messages:
        if hasattr(m, "type"):
            if m.type == "ai" and m.content:
                ai_response = m.content
            elif m.type == "tool" and m.content:
                try:
                    data = json.loads(m.content)
                    if data.get("type") == "overall_feeling":
                        overall = data["rating"]
                        next_phase = "symptom_screening"
                    elif data.get("type") == "symptom":
                        new_symptoms.append(data)
                        next_phase = "deep_dive"
                    elif data.get("type") == "no_symptoms":
                        next_phase = "closing"
                    elif data.get("type") == "complete":
                        complete = True
                except (json.JSONDecodeError, TypeError):
                    pass

    # Auto-advance phases
    if phase == "greeting" and not overall:
        next_phase = "overall_feeling"
    elif phase == "overall_feeling" and overall:
        next_phase = "symptom_screening"
    elif phase == "deep_dive" and next_phase == "deep_dive":
        next_phase = "summary"

    logger.info(
        "Check-in conversation node: phase=%s -> %s, symptoms=%d",
        phase, next_phase, len(new_symptoms),
    )

    return {
        "messages": result_messages,
        "phase": next_phase,
        "overall_feeling": overall,
        "reported_symptoms": new_symptoms,
        "session_complete": complete,
        "ai_response": ai_response,
    }


# ─── Graph builder ───


def build_checkin_graph():
    """Build and compile the check-in LangGraph.

    Single-node graph that executes one conversational turn. State persistence
    is managed externally by the database rather than LangGraph's checkpointer.
    """
    graph = StateGraph(CheckinState)

    graph.add_node("conversation", conversation_node)
    graph.set_entry_point("conversation")
    graph.add_edge("conversation", END)

    compiled = graph.compile()
    logger.info("Check-in LangGraph compiled")
    return compiled
