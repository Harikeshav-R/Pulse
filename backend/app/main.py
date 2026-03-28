"""TrialPulse FastAPI application factory.

Creates the async FastAPI app with lifespan management for database,
Redis, event bus, and WebSocket infrastructure. All module routers
are included under /api/v1.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.config import settings
from app.events.bus import EventBus
from app.ws.manager import WebSocketManager

# ─── Logging ───
logging.basicConfig(
    level=logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ─── Module-level globals (set during lifespan) ───
async_engine = None
async_session_factory = None
redis_client: aioredis.Redis | None = None
event_bus: EventBus | None = None
ws_manager = WebSocketManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize and tear down shared resources."""
    global async_engine, async_session_factory, redis_client, event_bus

    logger.info("Starting TrialPulse backend (env=%s)", settings.ENVIRONMENT)

    # ── Database ──
    async_engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.ENVIRONMENT == "development",
        pool_size=20,
        max_overflow=10,
    )
    async_session_factory = async_sessionmaker(
        async_engine,
        expire_on_commit=False,
    )
    logger.info("Database engine created: %s", settings.DATABASE_URL.split("@")[-1])

    # ── Redis ──
    redis_client = aioredis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
    )
    await redis_client.ping()
    logger.info("Redis connected: %s", settings.REDIS_URL)

    # ── Event Bus ──
    event_bus = EventBus(redis_client)
    _register_event_handlers(event_bus)
    listener_task = asyncio.create_task(
        event_bus.start_listening(),
        name="event_bus_listener",
    )
    logger.info("EventBus listener started")

    # ── Scheduler ──
    from app.scheduler import start_scheduler, stop_scheduler

    start_scheduler()

    yield

    # ── Shutdown ──
    logger.info("Shutting down TrialPulse backend")
    stop_scheduler()
    listener_task.cancel()
    await event_bus.stop()
    await redis_client.close()
    await async_engine.dispose()
    logger.info("All resources cleaned up")


def _register_event_handlers(bus: EventBus) -> None:
    """Register all event handlers from modules.

    This wires the decoupled event-driven architecture:
    checkin → alert engine, wearable → anomaly detection → alert engine, etc.
    """
    # Import lazily to avoid circular imports
    from app.modules.alert.service import (
        handle_symptom_reported,
        handle_anomaly_detected,
        handle_checkin_missed,
    )
    from app.modules.wearable.service import handle_wearable_data_received

    bus.subscribe("symptom.reported", handle_symptom_reported)
    bus.subscribe("anomaly.detected", handle_anomaly_detected)
    bus.subscribe("wearable.data_received", handle_wearable_data_received)
    bus.subscribe("checkin.missed", handle_checkin_missed)
    logger.info("Event handlers registered")


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(
        title="TrialPulse API",
        description="AI-powered clinical trial patient safety and engagement platform",
        version="0.1.0",
        lifespan=lifespan,
    )

    # ── CORS (permissive for hackathon) ──
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Register routers ──
    from app.modules.auth.router import router as auth_router
    from app.modules.checkin.router import router as checkin_router
    from app.modules.wearable.router import router as wearable_router
    from app.modules.alert.router import router as alert_router
    from app.modules.dashboard.router import router as dashboard_router
    from app.modules.analytics.router import router as analytics_router
    from app.modules.voice.router import router as voice_router
    from app.modules.patient.router import router as patient_router

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(checkin_router, prefix="/api/v1")
    app.include_router(wearable_router, prefix="/api/v1")
    app.include_router(alert_router, prefix="/api/v1")
    app.include_router(dashboard_router, prefix="/api/v1")
    app.include_router(analytics_router, prefix="/api/v1")
    app.include_router(voice_router, prefix="/api/v1")
    app.include_router(patient_router, prefix="/api/v1")

    # ── Health check ──
    @app.get("/api/v1/health", tags=["system"])
    async def health_check():
        """Check connectivity to all backing services."""
        checks = {}
        try:
            await redis_client.ping()
            checks["redis"] = "connected"
        except Exception:
            checks["redis"] = "disconnected"

        try:
            async with async_session_factory() as session:
                await session.execute(__import__("sqlalchemy").text("SELECT 1"))
                checks["postgres"] = "connected"
        except Exception:
            checks["postgres"] = "disconnected"

        checks["livekit"] = "configured" if settings.LIVEKIT_URL else "not_configured"

        status = (
            "ok"
            if all(v == "connected" for k, v in checks.items() if k != "livekit")
            else "degraded"
        )
        return {"status": status, "services": checks}

    # ── WebSocket endpoint for dashboard real-time updates ──
    @app.websocket("/ws/dashboard")
    async def dashboard_websocket(
        websocket: WebSocket,
        trial_id: str = Query(...),
        token: str = Query(default=""),
    ):
        """WebSocket for real-time dashboard updates, grouped by trial_id."""
        await ws_manager.connect(websocket, trial_id)
        try:
            while True:
                # Keep connection alive; client can send pings
                await websocket.receive_text()
        except WebSocketDisconnect:
            ws_manager.disconnect(websocket, trial_id)

    return app


app = create_app()
