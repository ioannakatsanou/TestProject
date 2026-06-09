"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://agfb:agfb@localhost:5432/agfb"
    anthropic_api_key: str = ""
    claude_model: str = "claude-haiku-4-5"
    allowed_origin: str = "http://localhost:3000"
    max_context_decisions: int = 12

    @property
    def mock_mode(self) -> bool:
        """When no API key is set, build answers deterministically from seed data."""
        return not self.anthropic_api_key.strip()


settings = Settings()
