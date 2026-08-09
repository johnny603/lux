import os
import tempfile
import json

import storage
import cli


def test_storage_roundtrip(tmp_path):
    path = tmp_path / "state.json"
    state = {"version": 1, "solved": {}}
    storage.save_state(state, str(path))
    loaded = storage.load_state(str(path))
    assert loaded.get("version") == 1


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
    # unsolved easy/medium/hard first (easy then medium then hard), then solved at end
    assert ordered[0]["id"] == "1"
    assert ordered[-1]["id"] == "2"
