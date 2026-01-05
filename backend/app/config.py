from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    fastf1_cache_dir: str = Field(
        default="./.fastf1cache", description="Directory for FastF1 on-disk cache."
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection string for async caching.",
    )

    # TTL defaults (seconds)
    ttl_calendar: int = Field(
        default=60 * 60 * 24, description="Cache duration for calendar responses."
    )
    ttl_event_detail: int = Field(
        default=60 * 60 * 8,
        description="Cache duration for event detail endpoints (6–12h recommended).",
    )
    ttl_session_results: int = Field(
        default=60 * 10,
        description="Cache duration for session result endpoints (5–15m recommended).",
    )
    ttl_telemetry: int = Field(
        default=60 * 60 * 24 * 2,
        description="Cache duration for telemetry endpoints (1–7d recommended).",
    )
    ttl_standings: int = Field(
        default=60 * 30,
        description="Cache duration for standings endpoints (15–60m recommended).",
    )
    ttl_profiles: int = Field(
        default=60 * 60 * 8,
        description="Cache duration for driver/team profile endpoints (6–12h recommended).",
    )

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
