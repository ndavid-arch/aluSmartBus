"""Tests that each role can only use its own features (issue #11)."""

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

from app.core.deps import AdminUser, DriverUser, StudentUser
from app.db import get_db
from tests.conftest import auth_headers

# Small routes that exist only in these tests, one per role
router = APIRouter()


@router.get("/student-only")
def student_only(user: StudentUser) -> dict[str, str]:
    """Answers only students."""
    return {"role": user.role.value}


@router.get("/driver-only")
def driver_only(user: DriverUser) -> dict[str, str]:
    """Answers only drivers."""
    return {"role": user.role.value}


@router.get("/admin-only")
def admin_only(user: AdminUser) -> dict[str, str]:
    """Answers only administrators."""
    return {"role": user.role.value}


@pytest.fixture
def role_client(db):
    """A client for a tiny app holding the routes above, using the test database."""
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = lambda: db
    return TestClient(app)


@pytest.mark.parametrize(
    ("path", "allowed_role"),
    [("/student-only", "student"), ("/driver-only", "driver"), ("/admin-only", "admin")],
)
def test_each_role_gets_only_its_own_routes(
    role_client, student, driver, admin, path, allowed_role
):
    """The matching role gets 200; every other role gets 403."""
    for user in (student, driver, admin):
        response = role_client.get(path, headers=auth_headers(user))
        expected = 200 if user.role.value == allowed_role else 403
        assert response.status_code == expected, f"{user.role.value} on {path}"


def test_student_cannot_use_admin_routes(role_client, student):
    """A student calling an admin route is refused with 403."""
    response = role_client.get("/admin-only", headers=auth_headers(student))
    assert response.status_code == 403
    assert response.json()["detail"] == "This is not available for your role"


def test_role_routes_still_require_sign_in(role_client):
    """Without a token the answer is 401 (not signed in), not 403."""
    assert role_client.get("/admin-only").status_code == 401
