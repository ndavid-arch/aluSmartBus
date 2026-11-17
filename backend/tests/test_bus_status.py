"""Tests for marking buses Available or Unavailable (issue #14)."""

import uuid

from sqlalchemy import func, select

from app.models import Notification
from tests.conftest import auth_headers


def mark(client, user, bus_id, availability, reason=None):
    """Change a bus's status as the given user and return the response."""
    return client.patch(
        f"/buses/{bus_id}/availability",
        json={"availability": availability, "reason": reason},
        headers=auth_headers(user),
    )


def test_anyone_can_see_bus_status_without_signing_in(client, bus):
    """The bus list is public, and it never shows the secret QR code."""
    response = client.get("/buses")
    assert response.status_code == 200
    [listed] = response.json()
    assert listed["plate_number"] == "RAB 123 A"
    assert listed["availability"] == "available"
    assert "qr_code" not in listed


def test_admin_marks_a_bus_unavailable_with_a_reason(client, admin, bus):
    """Given I am an admin, when I mark a bus Unavailable with a reason, then students see both."""
    response = mark(client, admin, bus["id"], "unavailable", "  Flat tyre  ")
    assert response.status_code == 200
    seen = client.get(f"/buses/{bus['id']}").json()
    assert seen["availability"] == "unavailable"
    assert seen["unavailable_reason"] == "Flat tyre"


def test_a_driver_can_change_the_status(client, driver, bus):
    """Drivers are authorised to mark buses too."""
    assert mark(client, driver, bus["id"], "unavailable", "Engine check").status_code == 200


def test_students_and_guests_cannot_change_the_status(client, student, bus):
    """A student gets 403 and someone not signed in gets 401."""
    assert mark(client, student, bus["id"], "unavailable").status_code == 403
    no_sign_in = client.patch(
        f"/buses/{bus['id']}/availability", json={"availability": "available"}
    )
    assert no_sign_in.status_code == 401


def test_reason_is_cleared_when_the_bus_runs_again(client, admin, bus):
    """An old reason must not show once the bus is Available again."""
    mark(client, admin, bus["id"], "unavailable", "Flat tyre")
    response = mark(client, admin, bus["id"], "available", "Flat tyre")
    assert response.json()["unavailable_reason"] is None


def test_reason_is_optional_and_limited_in_length(client, admin, bus):
    """No reason (or only spaces) is allowed; more than 200 characters is refused."""
    assert mark(client, admin, bus["id"], "unavailable", "   ").json()["unavailable_reason"] is None
    assert mark(client, admin, bus["id"], "unavailable", "x" * 201).status_code == 422


def test_unknown_bus_is_not_found(client, admin):
    """A bus ID that does not exist gives 404 for reading and for changing."""
    missing = uuid.uuid4()
    assert client.get(f"/buses/{missing}").status_code == 404
    assert mark(client, admin, missing, "unavailable").status_code == 404


def test_no_notification_is_sent_when_the_status_changes(client, db, admin, bus):
    """Students only see the status when they look; nobody is notified unasked (FR-51)."""
    mark(client, admin, bus["id"], "unavailable", "Flat tyre")
    assert db.scalar(select(func.count()).select_from(Notification)) == 0
