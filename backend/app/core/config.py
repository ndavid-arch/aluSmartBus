"""App settings, read from environment variables or the .env file."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Every setting the app needs. Each one can be set as an environment variable."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "ALU SmartBus API"
    database_url: str
    secret_key: str
    access_token_minutes: int = 720  # 12 hours: a school day without signing in again
    student_email_domain: str = "alustudent.com"  # only these emails may sign up as students
    location_accuracy_limit_m: float = 30  # readings less precise than this are not saved (#9)
    average_bus_speed_kmh: float = 20  # for ETAs; refine with real journey data after the pilot
    off_route_distance_m: float = 400  # farther than this from the route: "Not on the route yet"
    local_utc_offset_hours: int = 2  # Kigali is UTC+2 all year; report dates are local days (#30)
    # The websites allowed to call the API from a browser once deployed, comma-separated (#32),
    # e.g. "https://alusmartbus.onrender.com". Locally the dev server's proxy is used instead.
    cors_origins: str = ""

    @field_validator("database_url")
    @classmethod
    def use_psycopg(cls, url: str) -> str:
        """Hosts such as Neon give "postgresql://..." or "postgres://..."; SQLAlchemy needs to be
        told to use the psycopg driver the app installs."""
        for prefix in ("postgres://", "postgresql://"):
            if url.startswith(prefix):
                return "postgresql+psycopg://" + url.removeprefix(prefix)
        return url

    @property
    def allowed_origins(self) -> list[str]:
        """cors_origins as a list, without blanks or trailing slashes."""
        return [o.strip().rstrip("/") for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Read the settings once and reuse them everywhere."""
    return Settings()
