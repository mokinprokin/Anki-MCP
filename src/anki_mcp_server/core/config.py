from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .logger import logger

BASE_DIR = Path(__file__).parent


def resolve_env_file() -> Path | None:
    env_file = BASE_DIR / ".env"
    example_file = BASE_DIR / ".env.example"

    if env_file.exists():
        return env_file

    if example_file.exists():
        logger.warning(
            "\n"
            "⚠️  [WARNING]: .env file not found!\n"
            "⚠️  Falling back to template configuration (.env.example).\n"
            "⚠️  Create a .env file to override default settings.\n\n"
        )
        return example_file

    return None


class Settings(BaseSettings):
    anki_connect_url: str = Field(
        default="http://127.0.0.1:8765",
    )
    default_deck: str = Field(
        default="English",
    )
    request_timeout: int = Field(default=5)
    instructions_filename: str = Field(default="INSTRUCTIONS.md")

    model_config = SettingsConfigDict(
        env_file=resolve_env_file(), env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
