"""Tests for drawing the route along the real roads (issue #79)."""

import io
import json

import pytest

from app import road_path
from app.road_path import (
    load_road_path,
    path_from_answer,
    routing_url,
    stops_off_the_path,
    waypoints,
)
from app.routers import live
from app.seed_data import STOPS

REBERO, RUJUGIRO = STOPS[0], STOPS[1]


def answer(points):
    """What the routing engine sends back for a path of (latitude, longitude) points."""
    coordinates = [[lng, lat] for lat, lng in points]
    return {"code": "Ok", "routes": [{"geometry": {"coordinates": coordinates}}]}


# --- Box 1: fetched once by a script and saved ---------------------------------------------


def test_via_points_go_after_their_stop():
    """A via point after Rebero sits between Rebero and Rujugiro."""
    via = {0: [(-1.988, 30.07)]}
    points = waypoints(stops=[REBERO, RUJUGIRO], via=via)
    assert points == [(REBERO[1], REBERO[2]), (-1.988, 30.07), (RUJUGIRO[1], RUJUGIRO[2])]


def test_the_request_puts_longitude_first():
    """OSRM wants 'longitude,latitude' and the full road geometry."""
    url = routing_url([(-1.99, 30.06), (-1.98, 30.07)])
    assert "30.06,-1.99;30.07,-1.98" in url
    assert "overview=full" in url and "geometries=geojson" in url


def test_the_answer_becomes_latitude_longitude_points():
    """GeoJSON is [longitude, latitude]; the app uses (latitude, longitude)."""
    assert path_from_answer(answer([(-1.99, 30.06), (-1.98, 30.07)])) == [
        (-1.99, 30.06),
        (-1.98, 30.07),
    ]


def test_no_route_is_a_clear_error():
    """The script stops instead of saving an empty path."""
    with pytest.raises(ValueError, match="no route"):
        path_from_answer({"code": "NoRoute", "message": "Impossible route", "routes": []})


def test_the_script_saves_the_path(monkeypatch, tmp_path, capsys):
    """One request, one file; the stops are checked against the path."""
    path = [(lat, lng) for _, lat, lng in STOPS]
    monkeypatch.setattr(road_path, "PATH_FILE", tmp_path / "data" / "road_path.json")
    monkeypatch.setattr(
        road_path, "urlopen", lambda url, timeout: io.BytesIO(json.dumps(answer(path)).encode())
    )
    assert road_path.main() == 0
    saved = json.loads((tmp_path / "data" / "road_path.json").read_text())
    assert [tuple(p) for p in saved["points"]] == path
    assert "Saved 13 points" in capsys.readouterr().out


# --- Box 3: checked against the real route ---------------------------------------------------


def test_a_stop_far_from_the_path_is_reported():
    """The path skips Rujugiro, so the script says to check it."""
    path = [(REBERO[1], REBERO[2])]
    far = stops_off_the_path(path, stops=[REBERO, RUJUGIRO])
    assert [name for name, _ in far] == ["Rujugiro"]


def test_stops_on_the_path_are_fine():
    """A path through every stop needs no via points."""
    assert stops_off_the_path([(lat, lng) for _, lat, lng in STOPS]) == []


# --- Box 2: /route returns it and the map draws it -------------------------------------------


def test_without_a_saved_path_the_line_joins_the_stops(client, route, monkeypatch):
    """Before the script has run, the map draws straight lines as before."""
    monkeypatch.setattr(live, "load_road_path", lambda: None)
    body = client.get("/route").json()
    assert body["path"] == [[stop["latitude"], stop["longitude"]] for stop in body["stops"]]


def test_the_saved_road_path_is_what_the_map_draws(client, route, monkeypatch):
    """Once saved, /route sends the road path instead."""
    road = [(-1.99, 30.06), (-1.989, 30.065), (-1.985, 30.075)]
    monkeypatch.setattr(live, "load_road_path", lambda: road)
    assert client.get("/route").json()["path"] == [list(p) for p in road]


def test_the_saved_file_is_read(monkeypatch, tmp_path):
    """The file holds [latitude, longitude] pairs; a missing file means no road path yet."""
    file = tmp_path / "road_path.json"
    monkeypatch.setattr(road_path, "PATH_FILE", file)
    load_road_path.cache_clear()
    assert load_road_path() is None
    load_road_path.cache_clear()
    file.write_text(json.dumps({"points": [[-1.99, 30.06]]}))
    assert load_road_path() == [(-1.99, 30.06)]
    load_road_path.cache_clear()
