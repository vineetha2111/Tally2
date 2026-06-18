"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the AI Analytics application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = Field(
        default="postgresql://tally_user:tally_password@localhost:5432/tally_db",
        description="PostgreSQL connection URL",
    )
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama server base URL",
    )
    ollama_model: str = Field(
        default="qwen3:8b",
        description="Ollama model name (qwen3:8b, llama3.1:8b, deepseek-r1:8b)",
    )
    ollama_temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    ollama_timeout: int = Field(default=120, ge=10)
    log_level: str = Field(default="INFO")
    sql_row_limit: int = Field(default=1000, ge=1)
    schema_max_tables: int = Field(default=20, ge=1)


@lru_cache
def get_settings() -> Settings:
    """Return cached settings singleton."""
    return Settings()
