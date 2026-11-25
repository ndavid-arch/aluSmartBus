"""Tests for the admin's journey, boarding and demand report (issue #30)."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from app.models import Journey, Role, StopArrival
from app.seed_data import STOPS
from tests.conftest import auth_headers

REMERA, KIMIRONKO = STOPS[8], STOPS[9]
# 08:00 in Kigali on 25 November 2026 (Kigali is UTC+2)
MORNING = datetime(2026, 11, 25, 6, 0, tzinfo=UTC)


def report(client, admin, start="2026-11-25", end="2026-11-25"):
    """Ask for the report of a period."""
    url = f"/admin/reports?start={start}&end={end}"
    return client.get(url, headers=auth_headers(admin))


def by_name(stops: list[dict]) -> dict[str, dict]:
    """The demand rows keyed by stop name."""
    return {stop["name"]: stop for stop in stops}


class Trip:
    """Drive one journey through the API: choices, scans, then the end."""

    def __init__(self, client, db, driver, bus):
        self.client, self.db, self.driver, self.bus = client, db, driver, bus
        choice = {"bus_id": bus["id"], "direction": "rebero_to_alu"}
        self.journey = client.post("/journeys", json=choice, headers=auth_headers(driver)).json()
        self.stop_ids = {
            s["name"]: s["id"] for s in client.get(f"/journeys/{self.journey['id']}/stops").json()
        }

    def choose(self, student, kind, stop):
        """A student chooses a pickup or drop-off stop."""
        self.client.put(
            f"/journeys/{self.journey['id']}/selections/{kind}",
            json={"stop_id": self.stop_ids[stop[0]]},
            headers=auth_headers(student),
        )

    def board(self, student):
        """A student scans the QR code (#27)."""
        body = {"qr_code": self.bus["qr_code"]}
        self.client.post("/boardings", json=body, headers=auth_headers(student))

    def miss_at(self, stop):
        """The bus reaches the stop and the window closes with nobody boarding (#23)."""
        _, lat, lng = stop
        reading = {"latitude": lat, "longitude": lng, "accuracy": 5}
        url = f"/journeys/{self.journey['id']}/locations"
        self.client.post(url, json=reading, headers=auth_headers(self.driver))
        for arrival in self.db.scalars(select(StopArrival)):
            arrival.arrived_at = datetime.now(UTC) - timedelta(minutes=4)
        self.db.commit()

    def end(self, started_at=MORNING):
        """The driver ends the journey, and it is dated to the given start time."""
        url = f"/journeys/{self.journey['id']}/end"
        self.client.post(url, headers=auth_headers(self.driver))
        saved = self.db.get(Journey, uuid.UUID(self.journey["id"]))
        saved.started_at = started_at
        self.db.commit()


@pytest.fixture
def students(make_user):
    """Three students."""
    return [make_user(Role.STUDENT, f"rider{n}@alustudent.com") for n in range(3)]


@pytest.fixture
def busy_morning(client, db, route, driver, bus, students):
    """One completed trip: 2 pickups at Remera (1 boarded, 1 missed), 1 walk-up boarding,
    and 1 drop-off at Kimironko."""
    trip = Trip(client, db, driver, bus)
    trip.choose(students[0], "pickup", REMERA)
    trip.choose(students[1], "pickup", REMERA)
    trip.choose(students[0], "dropoff", KIMIRONKO)
    trip.board(students[0])
    trip.miss_at(REMERA)
    trip.board(students[2])  # no stop chosen: still a boarding
    trip.end()
    return trip


# --- Box 2: completed journeys and boarding totals ----------------------------------------


def test_the_report_counts_completed_journeys_and_boardings(client, admin, busy_morning, bus):
    """One trip, two students on board (FR-57)."""
    body = report(client, admin).json()
    assert body["completed_journeys"] == 1
    assert body["boardings"] == 2
    [row] = body["journeys"]
    assert row["plate_number"] == bus["plate_number"]
    assert row["boarded"] == 2
    assert row["ended_at"] is not None


def test_occupancy_is_boardings_over_seats(client, admin, busy_morning, bus):
    """2 students on a 30-seat bus."""
    assert report(client, admin).json()["average_occupancy"] == round(2 / bus["capacity"], 3)


def test_journeys_still_on_the_road_are_not_in_the_report(client, db, admin, route, driver, bus):
    """Only completed journeys count; today's running trip is not finished yet."""
    trip = Trip(client, db, driver, bus)
    db.get(Journey, uuid.UUID(trip.journey["id"])).started_at = MORNING
    db.commit()
    assert report(client, admin).json()["completed_journeys"] == 0


# --- Box 1: the chosen dates --------------------------------------------------------------


def test_journeys_outside_the_period_are_left_out(client, admin, busy_morning):
    """The trip is on the 25th, so a report for the 26th is empty."""
    body = report(client, admin, "2026-11-26", "2026-11-30").json()
    assert body["completed_journeys"] == 0
    assert body["average_occupancy"] is None


def test_the_end_date_is_included(client, admin, busy_morning):
    """A report from the 20th to the 25th includes the 25th."""
    assert report(client, admin, "2026-11-20", "2026-11-25").json()["completed_journeys"] == 1


def test_days_are_kigali_days_not_utc_days(client, db, admin, route, driver, bus):
    """00:30 in Kigali on the 25th is still the 24th in UTC: it belongs to the 25th."""
    trip = Trip(client, db, driver, bus)
    trip.end(started_at=datetime(2026, 11, 24, 22, 30, tzinfo=UTC))
    assert report(client, admin, "2026-11-25", "2026-11-25").json()["completed_journeys"] == 1
    assert report(client, admin, "2026-11-24", "2026-11-24").json()["completed_journeys"] == 0


@pytest.mark.parametrize(
    "query",
    [
        "start=2026-11-25&end=2026-11-24",  # ends before it starts
        "start=2025-01-01&end=2026-11-25",  # longer than a year
        "start=2026-13-01&end=2026-11-25",  # not a date
        "start=2026-11-25",  # no end date
    ],
)
def test_impossible_periods_are_refused(client, admin, query):
    """The admin gets a clear 422 instead of an empty report."""
    assert client.get(f"/admin/reports?{query}", headers=auth_headers(admin)).status_code == 422


# --- Box 3: demand by stop ----------------------------------------------------------------


def test_demand_is_summarised_by_stop(client, admin, busy_morning):
    """Pickups (boarded or missed) and drop-offs chosen at each stop (FR-58)."""
    stops = by_name(report(client, admin).json()["stops"])
    assert stops["Remera Gare"]["pickups"] == 2
    assert stops["Remera Gare"]["boarded"] == 1
    assert stops["Remera Gare"]["missed"] == 1
    assert stops["Kimironko Gare"]["dropoffs"] == 1
    assert (stops["Zindiro"]["pickups"], stops["Zindiro"]["dropoffs"]) == (0, 0)


def test_every_stop_is_listed_in_route_order(client, admin, busy_morning):
    """Even unused stops appear, so the admin sees where nobody waits."""
    names = [stop["name"] for stop in report(client, admin).json()["stops"]]
    assert names == [name for name, _, _ in STOPS]


def test_missed_pickups_are_totalled(client, admin, busy_morning):
    """The headline number for planning."""
    assert report(client, admin).json()["missed_pickups"] == 1


# --- Box 4: only admins, and no student names ----------------------------------------------


def test_the_report_names_no_student(client, admin, busy_morning, students):
    """Totals only (FR-59): no student's name or email in the report."""
    text = report(client, admin).text
    for student in students:
        assert student.email not in text
        assert student.full_name not in text


def test_only_admins_see_reports(client, driver, student):
    """Student transport records are for authorised admins only (FR-59)."""
    url = "/admin/reports?start=2026-11-25&end=2026-11-25"
    assert client.get(url, headers=auth_headers(driver)).status_code == 403
    assert client.get(url, headers=auth_headers(student)).status_code == 403
    assert client.get(url).status_code == 401
