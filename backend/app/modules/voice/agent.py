"""LiveKit voice agent worker — Gemini Live powered check-in agent.

This module defines the voice agent that joins LiveKit rooms and conducts
symptom check-ins using Google Gemini Live for real-time voice interaction.

Per TECHNICAL_DOC §5.3, the voice pipeline:
  Voice → LiveKit → Gemini Live → Same LangGraph state machine → DB
"""

import logging

from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
)
from livekit.agents.voice import AgentSession, Agent
from livekit.plugins import google

from app.ai.prompts.checkin_system import CHECKIN_SYSTEM_PROMPT
from app.config import settings

logger = logging.getLogger(__name__)


class VoiceCheckinAgent:
    """Voice check-in agent using Gemini Live via LiveKit.

    Connects to a LiveKit room and conducts a voice-based symptom
    check-in conversation, feeding through the same conversational
    flow as the text-based check-in.
    """

    def __init__(self, protocol_context: dict | None = None):
        self.protocol_context = protocol_context or {}

    async def start(self, ctx: JobContext):
        """Connect to the room and start the voice agent session."""
        logger.info(
            "Voice agent starting: room=%s",
            ctx.room.name,
        )

        await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

        # Format the system prompt with trial context
        system_prompt = CHECKIN_SYSTEM_PROMPT.format(
            therapeutic_area=self.protocol_context.get("therapeutic_area", "clinical"),
            protocol_number=self.protocol_context.get("protocol_number", ""),
            expected_side_effects=str(self.protocol_context.get("expected_side_effects", [])),
            phase="voice check-in",
        )

        # Create Gemini Live model for voice interaction
        model = google.llm.LLM.with_gemini(
            model="gemini-2.5-flash",
            api_key=settings.GOOGLE_API_KEY,
        )

        agent = Agent(instructions=system_prompt)
        session = AgentSession(llm=model)

        await session.start(
            room=ctx.room,
            agent=agent,
        )

        logger.info("Voice agent session started: room=%s", ctx.room.name)


def run_voice_worker():
    """Entry point to run the LiveKit voice agent worker process."""
    agent = VoiceCheckinAgent()
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=agent.start,
            api_key=settings.LIVEKIT_API_KEY,
            api_secret=settings.LIVEKIT_API_SECRET,
            ws_url=settings.LIVEKIT_URL,
        )
    )
