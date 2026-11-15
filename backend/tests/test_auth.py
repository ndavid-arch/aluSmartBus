"""Tests for signing in and reading the signed-in user (issue #10)."""

from tests.conftest import TEST_PASSWORD


def login(client, email, password):
    """Send a sign-in request and return the response."""
    return client.post("/auth/login", json={"email": email, "password": password})


def test_valid_details_return_a_token_and_the_role(client, student):
    """Given valid details, when I log in, then I get a token and my role."""
    response = login(client, "student@alustudent.com", TEST_PASSWORD)
    assert response.status_code == 200
    assert response.json()["role"] == "student"
    assert response.json()["access_token"]


def test_email_is_matched_without_caring_about_capitals_or_spaces(client, student):
    """Typing the email with capitals or a trailing space still works."""
    assert login(client, " Student@ALUstudent.com ", TEST_PASSWORD).status_code == 200


def test_wrong_password_gives_an_error_and_no_token(client, student):
    """Given a wrong password, when I log in, then I get an error and no token."""
    response = login(client, "student@alustudent.com", "wrong-password")
    assert response.status_code == 401
    assert "access_token" not in response.json()


def test_unknown_email_gives_the_same_error_as_a_wrong_password(client, student):
    """Nobody can find out which emails have accounts."""
    unknown = login(client, "nobody@alustudent.com", TEST_PASSWORD)
    wrong = login(client, "student@alustudent.com", "wrong-password")
    assert unknown.status_code == wrong.status_code == 401
    assert unknown.json() == wrong.json()


def test_disabled_account_cannot_sign_in(client, db, student):
    """An account an admin has disabled is refused."""
    student.is_active = False
    db.commit()
    assert login(client, "student@alustudent.com", TEST_PASSWORD).status_code == 403


def test_me_returns_the_signed_in_user(client, student):
    """With a valid token, /auth/me says who I am, without the password hash."""
    token = login(client, "student@alustudent.com", TEST_PASSWORD).json()["access_token"]
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "student@alustudent.com"
    assert "password_hash" not in response.json()


def test_me_without_a_token_is_refused(client):
    """Protected endpoints answer 401 when nobody is signed in."""
    assert client.get("/auth/me").status_code == 401


def test_me_with_a_fake_token_is_refused(client):
    """A made-up token is refused."""
    response = client.get("/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401
