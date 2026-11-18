"""What a guest (someone not signed in) can and cannot reach (issue #33, FR-60, NFR-27)."""

import pytest


def test_guest_can_see_the_buses_and_their_status(client, bus):
    """The bus list and each bus's status are public, so guests can check the bus quickly."""
    assert client.get("/buses").status_code == 200
    assert client.get(f"/buses/{bus['id']}").status_code == 200


@pytest.mark.parametrize("path", ["/auth/me", "/journeys/active", "/admin/buses", "/admin/drivers"])
def test_guest_cannot_see_personal_or_staff_records(client, path):
    """Anything about a person, or for staff only, needs signing in."""
    assert client.get(path).status_code == 401
