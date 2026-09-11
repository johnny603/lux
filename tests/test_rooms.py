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


def test_inventory_pickup_and_use(client):
    # Check initial empty inventory
    res_inv = client.get("/api/v1/inventory")
    assert res_inv.status_code == 200
    inv_data = res_inv.get_json()
    assert inv_data["ok"] is True
    assert inv_data["inventory"] == []

    # Attempt to pickup static object fails
    res_bad_pickup = client.post("/api/v1/rooms/room-1/objects/obj-flickering-terminal/pickup")
    assert res_bad_pickup.status_code == 400

    # Pickup pickupable object succeeds
    res_pickup = client.post("/api/v1/rooms/room-1/objects/obj-brass-keycard/pickup")
    assert res_pickup.status_code == 200
    pdata = res_pickup.get_json()
    assert pdata["ok"] is True
    assert pdata["object_id"] == "obj-brass-keycard"
    assert "obj-brass-keycard" in pdata["inventory"]

    # Verify inventory endpoint reflects item
    res_inv2 = client.get("/api/v1/inventory")
    assert res_inv2.status_code == 200
    inv2_data = res_inv2.get_json()
    assert "obj-brass-keycard" in inv2_data["inventory"]
    assert len(inv2_data["items"]) == 1
    assert inv2_data["items"][0]["name"] == "Brass Keycard"

    # Use item in valid target
    res_use = client.post(
        "/api/v1/rooms/room-1/objects/obj-brass-keycard/use",
        json={"target_id": "obj-security-console"},
    )
    assert res_use.status_code == 200
    udata = res_use.get_json()
    assert udata["ok"] is True
    assert udata["success"] is True
    assert "swipe the Brass Keycard" in udata["message"]

    # Use item not in inventory fails
    res_use_missing = client.post("/api/v1/rooms/room-2/objects/obj-c-reference-manual/use")
    assert res_use_missing.status_code == 400
    assert "do not possess" in res_use_missing.get_json()["error"]

    # Test CLI formatting
    state = storage.load_state()
    inv_ids = storage.get_inventory(state)
    items = [rooms.find_object_across_rooms(i) for i in inv_ids]
    formatted = cli.format_inventory(items)
    assert "🎒 Player Inventory:" in formatted
    assert "Brass Keycard" in formatted


def test_adaptive_hints_progression_and_api(client):
    # Initial state: 0 attempts on puzzle-1 -> Level 1 unlocked, Level 2 and 3 locked
    res_hints = client.get("/api/v1/rooms/room-1/hints")
    assert res_hints.status_code == 200
    hdata = res_hints.get_json()
    assert hdata["room_id"] == "room-1"
    assert hdata["unlocked_hints_count"] == 1
    assert hdata["total_hints_count"] == 3
    assert hdata["max_unlocked_level"] == 1
    assert len(hdata["available_hints"]) == 1
    assert "Inspect the filesystem" in hdata["available_hints"][0]

    # Attempting to reveal locked Level 2 hint fails with 403
    res_reveal_locked = client.post("/api/v1/rooms/room-1/hints/2/reveal")
    assert res_reveal_locked.status_code == 403
    assert "still locked" in res_reveal_locked.get_json()["error"]

    # Revealing Level 1 succeeds and records hint usage in storage
    res_reveal_1 = client.post("/api/v1/rooms/room-1/hints/1/reveal")
    assert res_reveal_1.status_code == 200
    r1_data = res_reveal_1.get_json()
    assert r1_data["ok"] is True
    assert r1_data["hint_level"] == 1
    assert "Inspect the filesystem" in r1_data["text"]

    state = storage.load_state()
    hints_used = storage.get_hints_used(state, "room-1")
    assert len(hints_used) == 1
    assert hints_used[0]["level"] == 1

    # Simulate 1 failed attempt on puzzle 1 -> Level 2 unlocks
    storage.record_attempt(state, "1", correct=False)
    storage.save_state(state)

    res_hints2 = client.get("/api/v1/rooms/room-1/hints")
    hdata2 = res_hints2.get_json()
    assert hdata2["failed_attempts"] == 1
    assert hdata2["unlocked_hints_count"] == 2
    assert hdata2["max_unlocked_level"] == 2
    assert len(hdata2["available_hints"]) == 2
    assert "dot" in hdata2["hints"][1]["text"]

    # Revealing Level 2 hint now succeeds
    res_reveal_2 = client.post("/api/v1/rooms/room-1/hints/2/reveal")
    assert res_reveal_2.status_code == 200

    # Simulate 3 total failed attempts on puzzle 1 -> Level 3 (direct solution) unlocks
    storage.record_attempt(state, "1", correct=False)
    storage.record_attempt(state, "1", correct=False)
    storage.save_state(state)

    res_hints3 = client.get("/api/v1/rooms/room-1/hints")
    hdata3 = res_hints3.get_json()
    assert hdata3["failed_attempts"] == 3
    assert hdata3["unlocked_hints_count"] == 3
    assert hdata3["max_unlocked_level"] == 3
    assert len(hdata3["available_hints"]) == 3
    assert "ls -a" in hdata3["hints"][2]["text"]


def test_room_atmosphere_and_theming(client):
    # Test catalog contains theme, atmosphere description, sights, sounds, smells, and ASCII layout
    all_rooms = rooms.get_all_rooms()
    for rm in all_rooms:
        assert "theme" in rm
        assert "atmosphere" in rm
        atm = rm["atmosphere"]
        assert "sights" in atm
        assert "sounds" in atm
        assert "smells" in atm
        assert "ambient_text" in atm
        assert "ascii_art" in atm

    # Test API returns atmosphere details
    res = client.get("/api/v1/rooms")
    assert res.status_code == 200
    rdata = res.get_json()
    assert len(rdata) == 5
    assert rdata[0]["theme"] == "cyberpunk-terminal"
    assert "Phosphor-green" in rdata[0]["atmosphere"]["sights"]

    # Test CLI look around / atmosphere formatting
    atm_str = cli.format_room_atmosphere(all_rooms[0])
    assert "Atmosphere & Observation: The Antechamber" in atm_str
    assert "Theme: cyberpunk-terminal" in atm_str
    assert "Sights: Phosphor-green" in atm_str
    assert "Sounds: A steady electrical hum" in atm_str
    assert "Smells: Faint ozone" in atm_str
    assert "Room Map / Layout:" in atm_str
    assert "[CRT]" in atm_str
    assert "Visible Interactive Items:" in atm_str
    assert "Flickering Terminal" in atm_str


def test_rooms_map_and_navigation(client):
    # Test catalog model includes position coordinates and connected_rooms
    all_rooms = rooms.get_all_rooms()
    for rm in all_rooms:
        assert "position" in rm
        assert "x" in rm["position"]
        assert "y" in rm["position"]
        assert "connected_rooms" in rm
        assert isinstance(rm["connected_rooms"], list)

    # Test get_rooms_map internal logic
    map_data = rooms.get_rooms_map()
    assert "rooms" in map_data
    assert "connections" in map_data
    assert "current_room_id" in map_data
    assert "grid" in map_data
    assert len(map_data["rooms"]) == 5
    assert len(map_data["connections"]) == 4
    assert map_data["current_room_id"] == "room-1"

    # Test GET /api/v1/rooms/map endpoint
    res_map = client.get("/api/v1/rooms/map")
    assert res_map.status_code == 200
    m_json = res_map.get_json()
    assert len(m_json["rooms"]) == 5
    assert m_json["current_room_id"] == "room-1"
    assert m_json["grid"]["total_rooms"] == 5
    assert m_json["grid"]["escaped_count"] == 0

    # Test GET /api/v1/rooms/map with custom current_room_id query parameter
    res_custom = client.get("/api/v1/rooms/map?current_room_id=room-3")
    assert res_custom.status_code == 200
    assert res_custom.get_json()["current_room_id"] == "room-3"

    # Test CLI ASCII map renderer
    ascii_map = cli.format_room_map(map_data)
    assert "Facility Navigation Map" in ascii_map
    assert "Current Location: room-1" in ascii_map
    assert "The Antechamber" in ascii_map
    assert "The Compiler Laborat" in ascii_map
    assert "YOU ARE HERE" in ascii_map
    assert "LOCKED" in ascii_map
    assert "room-1 <===> room-2" in ascii_map

    # Test web /rooms page rendering SVG map elements
    res_web = client.get("/rooms")
    assert res_web.status_code == 200
    html_text = res_web.get_data(as_text=True)
    assert "Facility Navigation Map" in html_text
    assert "facilitySvgMap" in html_text
    assert "room-node" in html_text
    assert "scrollToRoom" in html_text


def test_secret_rooms_discovery_and_easter_eggs(client):
    # Secret rooms are not included in default list
    all_rooms = rooms.get_all_rooms()
    assert len(all_rooms) == 5
    assert all(not r.get("is_secret") for r in all_rooms)

    # All rooms including secrets can be fetched
    all_with_secrets = rooms.get_all_rooms(include_secrets=True)
    assert len(all_with_secrets) == 7
    secret_rooms = [r for r in all_with_secrets if r.get("is_secret")]
    assert len(secret_rooms) == 2
    assert secret_rooms[0]["id"] == "room-secret-1"
    assert secret_rooms[1]["id"] == "room-secret-2"

    # Initially discovered secrets is empty
    state = storage.load_state()
    assert storage.get_discovered_secret_rooms(state) == []

    # Discovering room-secret-1
    storage.discover_secret_room(state, "room-secret-1")
    assert storage.is_secret_room_discovered(state, "room-secret-1") is True
    assert len(storage.get_discovered_secret_rooms(state)) == 1
    storage.save_state(state)

    # Room is now accessible in get_all_rooms(state=state)
    accessible = rooms.get_all_rooms(state=state)
    assert len(accessible) == 6
    assert any(r["id"] == "room-secret-1" for r in accessible)

    # Check achievements unlocking master_secrets only after all secret rooms discovered
    import achievements
    ach_unlocked = achievements.evaluate_achievements(state)
    assert not any(a["id"] == "master_secrets" for a in ach_unlocked)

    # Discover second secret room
    storage.discover_secret_room(state, "room-secret-2")
    storage.save_state(state)
    ach_unlocked_2 = achievements.evaluate_achievements(state)
    assert any(a["id"] == "master_secrets" for a in ach_unlocked_2)
    assert "master_secrets" in state["achievements"]

    # Formatting helper for discovery
    disc_text = cli.format_secret_room_discovery(secret_rooms[0])
    assert "EASTER EGG FOUND" in disc_text
    assert "The Hidden Glitch Sanctuary" in disc_text


