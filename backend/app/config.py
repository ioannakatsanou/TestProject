"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://agfb:agfb@localhost:5432/agfb"
    anthropic_api_key: str = ""
    claude_model: str = "claude-haiku-4-5"
    # Comma-separated list of allowed frontend origins (no trailing slash).
    # Local dev default; in production set ALLOWED_ORIGINS to your Vercel URL(s).
    allowed_origins: str = "http://localhost:3000"
    max_context_decisions: int = 12

    @property
    def mock_mode(self) -> bool:
        """When no API key is set, build answers deterministically from seed data."""
        return not self.anthropic_api_key.strip()

    @property
    def cors_origins(self) -> list[str]:
        """Parse ALLOWED_ORIGINS into a clean list of origins."""
        return [o.strip().rstrip("/") for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()
