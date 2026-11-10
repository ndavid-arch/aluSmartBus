"""App settings, read from environment variables or the .env file."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Every setting the app needs. Each one can be set as an environment variable."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "ALU SmartBus API"
    database_url: str


@lru_cache
def get_settings() -> Settings:
    """Read the settings once and reuse them everywhere."""
    return Settings()