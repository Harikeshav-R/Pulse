"""Redis pub/sub event bus for decoupled in-process communication.

All module-to-module communication goes through this bus instead of
direct function calls, per AGENTS.md §4.1 event-driven architecture.
"""

import asyncio
import json
import logging
from typing import Any, Callable, Coroutine

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

CHANNEL = "trialpulse:events"


class EventBus:
    """Async event bus backed by Redis pub/sub.

    Modules publish events (e.g. 'symptom.reported') and other modules
    subscribe handlers that run as asyncio tasks when events arrive.
    """

    def __init__(self, redis: aioredis.Redis) -> None:
        self.redis = redis
        self._handlers: dict[str, list[Callable[..., Coroutine[Any, Any, None]]]] = {}
        self._pubsub: aioredis.client.PubSub | None = None
        self._listener_task: asyncio.Task | None = None

    async def publish(self, event_type: str, payload: dict) -> None:
        """Publish an event to all subscribers."""
        message = json.dumps({"type": event_type, "payload": payload})
        await self.redis.publish(CHANNEL, message)
        logger.info(
            "Event published: %s",
            event_type,
            extra={"event_type": event_type, "payload_keys": list(payload.keys())},
        )

    def subscribe(self, event_type: str, handler: Callable[..., Coroutine[Any, Any, None]]) -> None:
        """Register an async handler for an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.info(
            "Handler registered for event: %s -> %s",
            event_type,
            handler.__qualname__,
        )

    async def start_listening(self) -> None:
        """Background task: listen for Redis pub/sub messages and dispatch to handlers."""
        self._pubsub = self.redis.pubsub()
        await self._pubsub.subscribe(CHANNEL)
        logger.info("EventBus listener started on channel: %s", CHANNEL)

        async for message in self._pubsub.listen():
            if message["type"] != "message":
                continue
            try:
                data = json.loads(message["data"])
                event_type = data["type"]
                payload = data["payload"]
                handlers = self._handlers.get(event_type, [])

                if not handlers:
                    logger.debug("No handlers for event: %s", event_type)
                    continue

                logger.info(
                    "Dispatching event %s to %d handler(s)",
                    event_type,
                    len(handlers),
                )
                for handler in handlers:
                    asyncio.create_task(
                        self._safe_handle(handler, event_type, payload),
                        name=f"event:{event_type}:{handler.__qualname__}",
                    )
            except Exception:
                logger.exception("Failed to process event bus message")

    async def _safe_handle(
        self,
        handler: Callable[..., Coroutine[Any, Any, None]],
        event_type: str,
        payload: dict,
    ) -> None:
        """Execute handler with error logging so failures don't crash the bus."""
        try:
            await handler(payload)
        except Exception:
            logger.exception(
                "Event handler failed: %s for event %s",
                handler.__qualname__,
                event_type,
            )

    async def stop(self) -> None:
        """Cleanly shut down the listener."""
        if self._pubsub:
            await self._pubsub.unsubscribe(CHANNEL)
            await self._pubsub.close()
            logger.info("EventBus listener stopped")
