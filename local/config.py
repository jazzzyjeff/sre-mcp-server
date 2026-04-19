"""Anthropic configuration settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Anthropic connection settings."""

    anthropic_api_key: str

    class Config:
        """Pydantic config."""

        env_file = ".env"
        extra = "ignore"


settings = Settings()
