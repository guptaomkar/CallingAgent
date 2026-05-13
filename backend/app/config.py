# ============================================================
# AI Calling Agent — Application Configuration
# File: app/config.py
# ============================================================

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Database ---
    database_url: str = "postgresql+asyncpg://callagent:callagent_pass@localhost:5432/callagent_db"

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- OpenAI (GPT-4.1) ---
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1"

    # --- Vapi.ai Telephony ---
    vapi_api_key: str = ""
    vapi_phone_number_id: str = ""
    vapi_base_url: str = "https://api.vapi.ai"

    # --- Twilio (Fallback) ---
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    # --- ElevenLabs TTS ---
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = ""
    elevenlabs_model_id: str = "eleven_turbo_v2_5"

    # --- Deepgram STT ---
    deepgram_api_key: str = ""

    # --- Application ---
    app_name: str = "AI Calling Agent"
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # --- Campaign Defaults ---
    default_language: str = "English"
    max_concurrent_calls: int = 10
    max_retry_attempts: int = 3
    retry_interval_hours: int = 24
    max_call_duration_seconds: int = 300

    # --- Security ---
    secret_key: str = "change-this-in-production"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — reads .env once."""
    return Settings()
