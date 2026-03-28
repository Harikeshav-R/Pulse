"""Vendor-agnostic LLM factory via OpenRouter.

All LLM calls go through this abstraction per AGENTS.md §4.1.
OpenRouter provides access to multiple model providers through a single API.

Uses LangChain v1 `create_agent` for agent creation and `init_chat_model`
for direct model access when needed.
"""

import logging

from langchain.chat_models import init_chat_model

from app.config import settings

logger = logging.getLogger(__name__)


def get_chat_model(temperature: float = 0.7, max_tokens: int = 1024):
    """Return a LangChain-compatible chat model via OpenRouter.

    Uses init_chat_model for direct model usage (e.g. classification).
    For agent workflows, prefer create_agent from langchain.agents.
    """
    logger.debug("Creating chat model: model=%s, temp=%.1f", settings.LLM_MODEL, temperature)

    return init_chat_model(
        model=settings.LLM_MODEL,
        model_provider="openrouter",
        api_key=settings.OPENROUTER_API_KEY,
        temperature=temperature,
        max_tokens=max_tokens,
    )
