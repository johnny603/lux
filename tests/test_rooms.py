import pytest

import cli
import rooms
import storage
from server import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_state_file = str(tmp_path / "test_lux_state.json")
    monkeypatch.setenv(storage.DEFAULT_STATE_ENV, test_state_file)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_rooms_default_catalog():
    all_rooms = rooms.get_all_rooms()
    assert len(all_rooms) == 5
    assert all_rooms[0]["id"] == "room-1"
    assert all_rooms[0]["locked"] is False
    assert len(all_rooms[0]["objects"]) >= 2
    assert all_rooms[1]["locked"] is True


def test_room_objects_inspection():
    objs = rooms.get_room_objects("room-1")
    assert objs is not None
    assert len(objs) >= 2
    term = rooms.get_room_object("room-1", "obj-flickering-terminal")
    assert term is not None
    assert term["is_pickupable"] is False
    assert "Flickering Terminal" in term["name"]

    keycard = rooms.get_room_object("room-1", "obj-brass-keycard")
    assert keycard is not None
    assert keycard["is_pickupable"] is True


def test_interact_with_object():
    res = rooms.interact_with_object("room-1", "obj-flickering-terminal", action="examine")
    assert res is not None
    assert res["success"] is True
    assert "System Log" in res["message"]
    assert res["state_effect"] == "terminal_inspected"

    res_pickup = rooms.interact_with_object("room-1", "obj-brass-keycard", action="pickup")
    assert res_pickup is not None
    assert res_pickup["success"] is True
    assert res_pickup["is_pickupable"] is True
    assert "has_brass_keycard" == res_pickup["state_effect"]


def test_api_rooms_and_objects(client):
    res = client.get("/api/v1/rooms")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 5
    assert data[0]["is_unlocked"] is True
    assert "objects" in data[0]

    res_objs = client.get("/api/v1/rooms/room-1/objects")
    assert res_objs.status_code == 200
    objs = res_objs.get_json()
    assert len(objs) >= 2

    # Interact endpoint
    res_interact = client.post(
        "/api/v1/rooms/room-1/objects/obj-flickering-terminal/interact",
        json={"action": "examine"},
    )
    assert res_interact.status_code == 200
    idata = res_interact.get_json()
    assert idata["ok"] is True
    assert "System Log" in idata["message"]

    # 404 for non-existent room or object
    res_404_room = client.get("/api/v1/rooms/nonexistent/objects")
    assert res_404_room.status_code == 404

    res_404_obj = client.post(
        "/api/v1/rooms/room-1/objects/nonexistent/interact",
        json={"action": "examine"},
    )
    assert res_404_obj.status_code == 404


def test_cli_examine_formatting():
    objs = rooms.get_room_objects("room-1")
    formatted = cli.format_room_objects(objs)
    assert "Flickering Terminal" in formatted
    assert "[static]" in formatted
    assert "[pickupable]" in formatted

    examined = cli.examine_object(objs[0])
    assert "=== Flickering Terminal ===" in examined
    assert "Actions:" in examined


def test_timed_escape_pressure(client):
    from datetime import datetime, timedelta, timezone

    # Check room-2 timer initial state
    res = client.get("/api/v1/rooms/room-2")
    assert res.status_code == 200
    rdata = res.get_json()
    assert rdata["time_limit_seconds"] == 300

    # Room-1 escape unlocks room-2
    state = storage.load_state()
    storage.mark_room_escaped(state, "room-1")
    storage.save_state(state)

    # Unlock / Enter room-2 starts timer
    res_unlock = client.post("/api/v1/rooms/room-2/unlock")
    assert res_unlock.status_code == 200
    udata = res_unlock.get_json()
    assert udata["unlocked"] is True
    assert udata["timer"] is not None
    assert udata["timer"]["time_limit_seconds"] == 300
    assert udata["timer"]["is_expired"] is False

    # Simulate expired timer
    state = storage.load_state()
    past_iso = (datetime.now(timezone.utc) - timedelta(seconds=350)).isoformat()
    state["game"]["room_timers"]["room-2"]["started_at"] = past_iso
    storage.save_state(state)

    # Room-2 should now report expired and be locked
    res_expired = client.get("/api/v1/rooms/room-2")
    assert res_expired.status_code == 200
    ex_data = res_expired.get_json()
    assert ex_data["status"] == "expired"
    assert ex_data["is_unlocked"] is False
    assert ex_data["is_expired"] is True
    assert "Reset room" in ex_data["unlock_instruction"]

    # Unlock attempt fails when expired
    res_fail_unlock = client.post("/api/v1/rooms/room-2/unlock")
    assert res_fail_unlock.status_code == 403

    # Reset room-2 restores timer
    res_reset = client.post("/api/v1/rooms/room-2/reset")
    assert res_reset.status_code == 200
    reset_data = res_reset.get_json()
    assert reset_data["ok"] is True
    assert reset_data["timer"]["is_expired"] is False
    assert reset_data["timer"]["remaining_seconds"] > 290

    # Format timer CLI check
    timer_str = cli.format_room_timer(reset_data["timer"])
    assert "remaining" in timer_str
    assert "300s" in timer_str
