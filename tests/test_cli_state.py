import json

import cli
import storage


def test_storage_roundtrip(tmp_path):
    path = tmp_path / "state.json"
    state = {"version": 1, "solved": {}}
    storage.save_state(state, str(path))
    loaded = storage.load_state(str(path))
    assert loaded.get("version") >= 2


def test_loads_legacy_state_format(tmp_path):
    path = tmp_path / "state.json"
    path.write_text(json.dumps({"solved": ["1", "2"], "achievements": {}}))
    loaded = storage.load_state(str(path))
    assert loaded["version"] >= 2
    assert set(loaded["solved"].keys()) == {"1", "2"}


def test_mark_solved_and_get(tmp_path):
    path = tmp_path / "state.json"
    state = storage.load_state(str(path))
    storage.mark_solved(state, "1", attempts=2)
    storage.save_state(state, str(path))
    loaded = storage.load_state(str(path))
    assert "1" in loaded.get("solved", {})
    entry = loaded["solved"]["1"]
    assert entry.get("attempts") >= 2


def test_sort_levels_respects_difficulty_and_solved():
    levels = [
        {"id": "1", "title": "A", "difficulty": "medium"},
        {"id": "2", "title": "B", "difficulty": "easy"},
        {"id": "3", "title": "C", "difficulty": "hard"},
    ]
    solved = {"2"}
    ordered = cli.sort_levels(levels, solved)
    assert ordered[0]["id"] == "1"
    assert ordered[-1]["id"] == "2"


def test_progress_summary_tracks_streak(tmp_path):
    state = storage.default_state()
    storage.mark_solved(state, "1", at="2026-08-06T10:00:00+00:00")
    storage.mark_solved(state, "2", at="2026-08-07T10:00:00+00:00")
    storage.mark_solved(state, "3", at="2026-08-07T11:00:00+00:00")

    summary = storage.get_progress_summary(
        state, [{"id": "1"}, {"id": "2"}, {"id": "3"}, {"id": "4"}]
    )

    assert summary["solved_count"] == 3
    assert summary["current_streak"] == 2
    assert summary["longest_streak"] == 2
    assert summary["percent_complete"] == 75.0
