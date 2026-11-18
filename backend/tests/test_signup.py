"""Tests for students creating their own accounts (issue #48)."""

import pytest

from tests.conftest import TEST_PASSWORD

NEW_STUDENT = {
    "full_name": "Aline Uwase",
    "email": "a.uwase@alustudent.com",
    "password": TEST_PASSWORD,
}


def sign_up(client, **changes):
    """Send the sign-up form, with any field changed, and return the response."""
    return client.post("/auth/signup", json={**NEW_STUDENT, **changes})


def test_student_signs_up_and_is_signed_in(client):
    """Given valid details, a student account is created and its token works straight away."""
    response = sign_up(client)
    assert response.status_code == 201
    assert response.json()["role"] == "student"
    token = response.json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json()["email"] == "a.uwase@alustudent.com"


def test_new_student_can_sign_in_later(client):
    """The password chosen at sign-up works on the sign-in screen."""
    sign_up(client)
    login = client.post(
        "/auth/login", json={"email": NEW_STUDENT["email"], "password": TEST_PASSWORD}
    )
    assert login.status_code == 200


def test_email_is_tidied(client):
    """Spaces and capitals are ignored, the same way as at sign-in."""
    response = sign_up(client, email="  A.Uwase@ALUstudent.com ")
    assert response.status_code == 201


@pytest.mark.parametrize(
    "email",
    [
        "aline@gmail.com",
        "driver@alueducation.com",
        "aline@evil.alustudent.com",
        "aline@alustudent.com.evil.com",
        "aline@x@alustudent.com",
    ],
)
def test_only_alu_student_emails_can_sign_up(client, email):
    """Any other address is refused, including look-alikes."""
    response = sign_up(client, email=email)
    assert response.status_code == 422


def test_refusal_says_which_email_to_use(client):
    """The message tells the student what to do."""
    message = sign_up(client, email="aline@gmail.com").json()["detail"][0]["msg"]
    assert "@alustudent.com" in message


def test_email_already_used_is_refused(client, student):
    """An email that already has an account cannot sign up again."""
    response = sign_up(client, email=student.email)
    assert response.status_code == 409


@pytest.mark.parametrize("changes", [{"password": "short"}, {"full_name": "   "}])
def test_short_password_or_blank_name_is_refused(client, changes):
    """Passwords need at least 8 characters, and a name is required."""
    assert sign_up(client, **changes).status_code == 422


def test_sign_up_always_makes_a_student(client):
    """Sending a role is ignored, so nobody can sign themselves up as an admin or driver."""
    response = sign_up(client, role="admin")
    assert response.json()["role"] == "student"
