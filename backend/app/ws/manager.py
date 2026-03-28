"""WebSocket connection manager for real-time dashboard updates.

Maintains per-trial connection pools and broadcasts events (new alerts,
risk score changes, check-in completions) to all connected dashboard clients.
"""

import json
import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections grouped by trial_id."""

    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, trial_id: str) -> None:
        """Accept a WebSocket connection and register it for a trial."""
        await websocket.accept()
        if trial_id not in self._connections:
            self._connections[trial_id] = set()
        self._connections[trial_id].add(websocket)
        logger.info(
            "WebSocket connected for trial %s (total: %d)",
            trial_id,
            len(self._connections[trial_id]),
        )

    def disconnect(self, websocket: WebSocket, trial_id: str) -> None:
        """Remove a WebSocket connection."""
        if trial_id in self._connections:
            self._connections[trial_id].discard(websocket)
            logger.info(
                "WebSocket disconnected for trial %s (remaining: %d)",
                trial_id,
                len(self._connections[trial_id]),
            )

    async def broadcast(self, trial_id: str, event_type: str, payload: dict) -> None:
        """Broadcast an event to all dashboard clients watching a trial."""
        message = json.dumps({"type": event_type, "payload": payload})
        connections = self._connections.get(trial_id, set())

        if not connections:
            return

        dead: set[WebSocket] = set()
        for ws in connections:
            try:
                await ws.send_text(message)
            except Exception:
                dead.add(ws)

        if dead:
            self._connections[trial_id] -= dead
            logger.warning(
                "Removed %d dead WebSocket connection(s) for trial %s",
                len(dead),
                trial_id,
            )

        logger.debug(
            "Broadcast %s to %d client(s) for trial %s",
            event_type,
            len(connections) - len(dead),
            trial_id,
        )
