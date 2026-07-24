"""Project configuration and environment settings."""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the backend service."""

    app_name: str = "Biomechanics Backend"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    environment: str = "development"
    debug: bool = True
    temp_dir: str = "tmp"
    request_timeout_seconds: int = 120
    cors_allowed_origins: str = (
        "http://localhost:3000,"
        "http://127.0.0.1:3000,"
        "http://localhost:4173,"
        "http://127.0.0.1:4173,"
        "http://localhost:5173,"
        "http://127.0.0.1:5173,"
        "http://localhost:5174,"
        "http://127.0.0.1:5174"
    )

    # Supabase settings.
    supabase_url: str = ""
    supabase_publishable_key: str = ""
    supabase_secret_key: str = ""
    # Legacy compatibility fields.
    supabase_service_key: str = ""
    supabase_anon_key: str = ""
    supabase_db_url: str = ""
    supabase_bucket: str = "videos"
    supabase_chat_bucket: str = "chat-media"
    supabase_posture_bucket: str = "Postura"
    supabase_posture_analysis_bucket: str = "Postura-analisis"
    squat_auth_required: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_allowed_origins_list(self) -> List[str]:
        """Return the configured CORS origins as a cleaned list."""
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
