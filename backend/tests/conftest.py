"""Shared test set-up: a throwaway database and an API client that uses it."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
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
def student(db):
    """A student account with a known password."""
    user = User(
        full_name="Test Student",
        email="student@alustudent.com",
        password_hash=hash_password(TEST_PASSWORD),
        role=Role.STUDENT,
    )
    db.add(user)
    db.commit()
    return user
