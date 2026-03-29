"""Run the LiveKit voice agent worker process.

This must be run as a separate process from the FastAPI backend.
The worker connects to the LiveKit server and dispatches voice
check-in agents to rooms as patients join.

Usage:
    uv run python scripts/run_voice_worker.py dev
"""

from app.modules.voice.agent import run_voice_worker

if __name__ == "__main__":
    run_voice_worker()
