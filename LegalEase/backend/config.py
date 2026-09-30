from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = "LegalEase"

    gemini_api_key: str = ""

    gemini_model: str = "gemini-3.8-flash"

    backend_url: str = "http://127.0.0.1:8000"

    max_input_chars: int = 30000

    max_output_tokens: int = 12000

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()