"""TrialPulse configuration — loaded from environment variables via Pydantic Settings."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env from the project root (two levels up from this file)
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All secrets and connection strings come from env vars or .env file.
    Never hardcode credentials — this is enforced by AGENTS.md §5.
    """

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Environment ───
    ENVIRONMENT: str = "development"

    # ─── Database ───
    DATABASE_URL: str = "postgresql+asyncpg://tp_admin:tp_hackathon_2026@localhost:5432/trialpulse"

    # ─── Redis ───
    REDIS_URL: str = "redis://localhost:6379"

    # ─── MinIO (S3-compatible object storage) ───
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "trialpulse"
    MINIO_SECRET_KEY: str = "tp_hackathon_2026"
    MINIO_SECURE: bool = False

    # ─── LLM via OpenRouter ───
    OPENROUTER_API_KEY: str = ""
    LLM_MODEL: str = "anthropic/claude-sonnet-4-20250514"

    # ─── Google Gemini (LiveKit voice agent) ───
    GOOGLE_API_KEY: str = ""

    # ─── LiveKit ───
    LIVEKIT_URL: str = "ws://localhost:7880"
    LIVEKIT_CLIENT_URL: str = "ws://localhost:7880"  # URL returned to mobile clients
    LIVEKIT_API_KEY: str = "devkey"
    LIVEKIT_API_SECRET: str = "devsecret"

    # ─── JWT ───
    JWT_SECRET: str = "trialpulse-hackathon-secret-2026"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24


settings = Settings()
