"""Tests for administrators creating driver accounts (issue #12)."""

from tests.conftest import auth_headers

NEW_DRIVER = {
    "full_name": "Jean Paul",
    "email": "Jean.Paul@alueducation.com",
    "phone": "0788000111",
}


def test_admin_creates_a_driver_who_can_then_sign_in(client, admin):
    """Given I am an admin, when I enter a driver's name and email, then a driver account exists."""
    response = client.post("/admin/drivers", json=NEW_DRIVER, headers=auth_headers(admin))
    assert response.status_code == 201
    created = response.json()
    assert created["role"] == "driver"
    assert created["email"] == "jean.paul@alueducation.com"
    login = client.post(
        "/auth/login",
        json={"email": "jean.paul@alueducation.com", "password": created["temporary_password"]},
    )
    assert login.status_code == 200
    assert login.json()["role"] == "driver"


def test_only_admins_can_create_drivers(client, student, driver):
    """Students and drivers are refused, so nobody can make a driver account for themselves."""
    for user in (student, driver):
        response = client.post("/admin/drivers", json=NEW_DRIVER, headers=auth_headers(user))
        assert response.status_code == 403


def test_creating_a_driver_needs_sign_in(client):
    """Without signing in the answer is 401."""
    assert client.post("/admin/drivers", json=NEW_DRIVER).status_code == 401


def test_email_already_used_is_refused(client, admin, student):
    """An email that already has an account cannot be reused."""
    taken = {**NEW_DRIVER, "email": student.email}
    response = client.post("/admin/drivers", json=taken, headers=auth_headers(admin))
    assert response.status_code == 409


def test_bad_name_or_email_is_refused(client, admin):
    """A blank name or an address without a domain is rejected before anything is saved."""
    for bad in ({**NEW_DRIVER, "full_name": "  "}, {**NEW_DRIVER, "email": "jean@"}):
        assert (
            client.post("/admin/drivers", json=bad, headers=auth_headers(admin)).status_code == 422
        )


def test_admin_sees_only_drivers_in_the_list(client, admin, student, driver):
    """The list holds drivers only, never students or admins, and no password hashes."""
    response = client.get("/admin/drivers", headers=auth_headers(admin))
    assert response.status_code == 200
    assert [d["email"] for d in response.json()] == [driver.email]
    assert "password_hash" not in response.json()[0]
