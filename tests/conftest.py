import json

import pytest

import server


@pytest.fixture
def app():
    """Flask application fixture configured for testing."""
    server.app.config.update(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
        }
    )
    return server.app


@pytest.fixture
def client(app):
    """Flask test client fixture bound to the app."""
    return app.test_client()


@pytest.fixture
def tmp_state(tmp_path, monkeypatch):
    """Temporary state file fixture that sets LUX_STATE and cleans up after test."""
    state_file = tmp_path / "state.json"
    monkeypatch.setenv("LUX_STATE", str(state_file))
    return state_file


@pytest.fixture
def puzzle_dir(tmp_path):
    """Fixture directory containing a sample minimal puzzle definition."""
    puzzles_path = tmp_path / "puzzles"
    puzzles_path.mkdir(parents=True, exist_ok=True)
    sample_puzzle = puzzles_path / "sample_puzzle.json"
    sample_puzzle.write_text(
        json.dumps(
            {
                "id": "test_1",
                "title": "Sample Test Puzzle",
                "description": "A sample puzzle for testing",
                "category": "linux",
                "difficulty": "easy",
                "solution": "ls -la",
            },
            indent=2,
        )
    )
    return puzzles_path
