"""Tests for administrators registering buses (issue #13)."""

import uuid

import pytest

from tests.conftest import auth_headers

NEW_BUS = {"plate_number": " rab 123  a ", "capacity": 30}


@pytest.fixture
def bus(client, admin):
    """A bus registered by the admin, as the API returned it."""
    return client.post("/admin/buses", json=NEW_BUS, headers=auth_headers(admin)).json()


def test_admin_registers_a_bus(client, admin):
    """A new bus gets an ID, a QR code, the tidied plate and its capacity."""
    response = client.post("/admin/buses", json=NEW_BUS, headers=auth_headers(admin))
    assert response.status_code == 201
    bus = response.json()
    assert uuid.UUID(bus["id"])
    assert bus["plate_number"] == "RAB 123 A"
    assert bus["capacity"] == 30
    assert bus["qr_code"]
    assert bus["availability"] == "available"


def test_each_bus_gets_its_own_id_and_qr_code(client, admin, bus):
    """Two buses never share an ID or a QR code."""
    other = {"plate_number": "RAC 456 B", "capacity": 25}
    second = client.post("/admin/buses", json=other, headers=auth_headers(admin)).json()
    assert second["id"] != bus["id"]
    assert second["qr_code"] != bus["qr_code"]


def test_same_plate_cannot_be_registered_twice(client, admin, bus):
    """The same plate written differently is still a duplicate."""
    again = {"plate_number": "Rab 123 a", "capacity": 20}
    response = client.post("/admin/buses", json=again, headers=auth_headers(admin))
    assert response.status_code == 409


@pytest.mark.parametrize(
    "bad",
    [
        {"plate_number": "   ", "capacity": 30},
        {"plate_number": "RAB 123 A", "capacity": 0},
        {"plate_number": "RAB 123 A", "capacity": -5},
        {"plate_number": "RAB 123 A", "capacity": 101},
    ],
)
def test_bad_plate_or_capacity_is_refused(client, admin, bad):
    """A blank plate or a capacity outside 1 to 100 is rejected before anything is saved."""
    response = client.post("/admin/buses", json=bad, headers=auth_headers(admin))
    assert response.status_code == 422


def test_admin_changes_capacity_and_qr_code_stays(client, admin, bus):
    """Capacity can be changed, while the ID and QR code are permanent."""
    response = client.patch(
        f"/admin/buses/{bus['id']}", json={"capacity": 40}, headers=auth_headers(admin)
    )
    assert response.status_code == 200
    changed = response.json()
    assert changed["capacity"] == 40
    assert changed["id"] == bus["id"]
    assert changed["qr_code"] == bus["qr_code"]


def test_changing_an_unknown_bus_is_not_found(client, admin):
    """A bus ID that does not exist gives 404."""
    response = client.patch(
        f"/admin/buses/{uuid.uuid4()}", json={"capacity": 40}, headers=auth_headers(admin)
    )
    assert response.status_code == 404


def test_only_admins_manage_buses(client, student, driver, bus):
    """Students and drivers get 403, and anyone not signed in gets 401."""
    for user in (student, driver):
        headers = auth_headers(user)
        assert client.post("/admin/buses", json=NEW_BUS, headers=headers).status_code == 403
        assert client.get("/admin/buses", headers=headers).status_code == 403
        change = client.patch(f"/admin/buses/{bus['id']}", json={"capacity": 5}, headers=headers)
        assert change.status_code == 403
    assert client.get("/admin/buses").status_code == 401


def test_bus_list_is_sorted_by_plate(client, admin, bus):
    """The list shows every bus in plate order."""
    other = {"plate_number": "RAA 001 A", "capacity": 25}
    client.post("/admin/buses", json=other, headers=auth_headers(admin))
    response = client.get("/admin/buses", headers=auth_headers(admin))
    assert [b["plate_number"] for b in response.json()] == ["RAA 001 A", "RAB 123 A"]
