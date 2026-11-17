"""Shared test set-up: a throwaway database and an API client that uses it."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, hash_password
from app.db import Base, get_db
from app.main import app
from app.models import Role, User

TEST_PASSWORD = "bus-to-campus"


@pytest.fixture
def db():
    """A fresh, empty in-memory database for each test."""
    # StaticPool keeps one connection, so the API and the test see the same in-memory data
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as session:
        yield session


@pytest.fixture
def client(db):
    """An API client whose requests use the test database instead of the real one."""
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def make_user(db):
    """Create a user with the given role and the test password."""

    def _make_user(role: Role, email: str) -> User:
        user = User(
            full_name=f"Test {role.value}",
            email=email,
            password_hash=hash_password(TEST_PASSWORD),
            role=role,
        )
        db.add(user)
        db.commit()
        return user

    return _make_user


@pytest.fixture
def student(make_user):
    """A student account with a known password."""
    return make_user(Role.STUDENT, "student@alustudent.com")


@pytest.fixture
def driver(make_user):
    """A driver account with a known password."""
    return make_user(Role.DRIVER, "driver@alueducation.com")


@pytest.fixture
def admin(make_user):
    """An administrator account with a known password."""
    return make_user(Role.ADMIN, "admin@alueducation.com")


def auth_headers(user: User) -> dict[str, str]:
    """Request headers for a signed-in user, for calling protected endpoints in tests."""
    return {"Authorization": f"Bearer {create_access_token(str(user.id), user.role.value)}"}


# The bus most tests use; the messy spacing checks that plates are tidied
NEW_BUS = {"plate_number": " rab 123  a ", "capacity": 30}


@pytest.fixture
def bus(client, admin):
    """A bus registered by the admin, as the API returned it."""
    return client.post("/admin/buses", json=NEW_BUS, headers=auth_headers(admin)).json()
