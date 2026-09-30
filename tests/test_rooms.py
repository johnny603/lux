import pytest

import game_systems
import rooms
import storage
from server import app


@pytest.fixture
def client(monkeypatch, tmp_path):
    state_file = tmp_path / "test_state.json"
    monkeypatch.setenv("LUX_STATE", str(state_file))
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        yield client


def test_rooms_catalog_structure():
    all_rooms = rooms.get_all_rooms()
    assert len(all_rooms) >= 3
    for r in all_rooms:
        assert "id" in r
        assert "name" in r
        assert "description" in r
        assert "difficulty" in r
        assert 1 <= r["difficulty"] <= 5
        assert "locked" in r
        assert "unlock_condition" in r
        assert "hints" in r
        assert isinstance(r["hints"], list)
        assert "escape_condition" in r
        assert "puzzle_id" in r["escape_condition"]


def test_room_unlock_progression():
    r1 = rooms.get_room("room-1")
    r2 = rooms.get_room("room-2")
    r3 = rooms.get_room("room-3")
    assert r1 is not None and r2 is not None and r3 is not None

    # Initially room-1 is unlocked (starter room), room-2 is locked
    assert rooms.is_room_unlocked(r1, []) is True
    assert rooms.is_room_unlocked(r2, []) is False

    # Escaping room-1 unlocks room-2
    assert rooms.is_room_unlocked(r2, ["room-1"]) is True
    assert rooms.is_room_unlocked(r3, ["room-1"]) is False

    # Escaping room-2 unlocks room-3
    assert rooms.is_room_unlocked(r3, ["room-1", "room-2"]) is True


def test_api_rooms_and_room_detail(client):
    res = client.get("/api/v1/rooms")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) >= 3

    # Check first room status
    first = data[0]
    assert first["id"] == "room-1"
    assert first["is_unlocked"] is True
    assert first["is_escaped"] is False
    assert first["status"] == "unlocked"

    # Check second room (locked initially)
    second = data[1]
    assert second["id"] == "room-2"
    assert second["is_unlocked"] is False
    assert second["status"] == "locked"
    assert "unlock_instruction" in second

    # Check specific room endpoint
    res_single = client.get("/api/v1/rooms/room-1")
    assert res_single.status_code == 200
    single_data = res_single.get_json()
    assert single_data["name"] == "The Antechamber"

    # 404 for unknown room
    res_unknown = client.get("/api/v1/rooms/non-existent-room")
    assert res_unknown.status_code == 404


def test_api_room_unlock_endpoint(client):
    # Attempting to unlock room-2 without escaping room-1 returns 403
    res = client.post("/api/v1/rooms/room-2/unlock")
    assert res.status_code == 403
    data = res.get_json()
    assert data["ok"] is False
    assert data["unlocked"] is False
    assert "error" in data

    # Unlocking starter room-1 returns 200
    res_starter = client.post("/api/v1/rooms/room-1/unlock")
    assert res_starter.status_code == 200
    data_starter = res_starter.get_json()
    assert data_starter["ok"] is True
    assert data_starter["unlocked"] is True

    # 404 for unknown room unlock
    res_unknown = client.post("/api/v1/rooms/non-existent/unlock")
    assert res_unknown.status_code == 404


def test_game_systems_solve_updates_room_escape():
    state = storage.default_state()
    level = {"id": "1", "difficulty": "easy"}

    # Solve level 1 corresponding to room-1 escape condition
    updated = game_systems.on_level_solved(state, level)
    escaped = storage.get_escaped_rooms(updated)
    assert "room-1" in escaped

    # Rooms summary shows room-1 as escaped and room-2 as unlocked
    summary = rooms.get_rooms_summary(escaped)
    r1 = next(r for r in summary if r["id"] == "room-1")
    r2 = next(r for r in summary if r["id"] == "room-2")
    assert r1["status"] == "escaped"
    assert r2["status"] == "unlocked"


def test_web_rooms_page(client):
    res = client.get("/rooms")
    assert res.status_code == 200
    assert b"Escape Rooms" in res.data
    assert b"The Antechamber" in res.data
    assert b"Facility Progression Route" in res.data
