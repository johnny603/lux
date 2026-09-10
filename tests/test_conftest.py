import json
import os

import storage


def test_conftest_fixtures(app, client, tmp_state, puzzle_dir):
    assert app.config["TESTING"] is True
    assert app.config["WTF_CSRF_ENABLED"] is False

    response = client.get("/health")
    assert response.status_code == 200

    assert os.getenv("LUX_STATE") == str(tmp_state)
    assert storage.default_state_path() == str(tmp_state)

    assert puzzle_dir.is_dir()
    sample_puzzle_file = puzzle_dir / "sample_puzzle.json"
    assert sample_puzzle_file.exists()
    data = json.loads(sample_puzzle_file.read_text())
    assert data["id"] == "test_1"
