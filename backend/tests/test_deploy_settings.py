"""Tests for the settings the deployed app needs (issue #32)."""

import pytest

from app.core.config import Settings


def settings(**values) -> Settings:
    """Settings from the given values only, ignoring any .env file."""
    return Settings(_env_file=None, secret_key="x" * 32, **values)


@pytest.mark.parametrize(
    ("given", "used"),
    [
        (
            "postgresql://u:p@ep-x.neon.tech/db?sslmode=require",
            "postgresql+psycopg://u:p@ep-x.neon.tech/db?sslmode=require",
        ),
        ("postgres://u:p@host/db", "postgresql+psycopg://u:p@host/db"),
        (
            "postgresql+psycopg://u:p@localhost:5432/smartbus",
            "postgresql+psycopg://u:p@localhost:5432/smartbus",
        ),
        ("sqlite://", "sqlite://"),
    ],
)
def test_host_database_urls_use_the_installed_driver(given, used):
    """Neon's and Render's URLs work as pasted, without editing them."""
    assert settings(database_url=given).database_url == used


def test_allowed_websites_are_read_from_a_comma_list():
    """Spaces and trailing slashes are forgiven; blanks are dropped."""
    shown = settings(
        database_url="sqlite://",
        cors_origins=" https://alusmartbus.onrender.com/ , http://localhost:5173,",
    )
    assert shown.allowed_origins == ["https://alusmartbus.onrender.com", "http://localhost:5173"]


def test_no_website_is_allowed_by_default():
    """Locally the dev proxy is used, so nothing needs to be allowed."""
    assert settings(database_url="sqlite://").allowed_origins == []


def test_an_unknown_website_gets_no_permission(client):
    """Without CORS_ORIGINS, a browser on another site is not told it may read the API."""
    response = client.get("/health", headers={"Origin": "https://evil.example.com"})
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers
