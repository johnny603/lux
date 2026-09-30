from pathlib import Path

import pytest

import server
import storage


@pytest.fixture
def app_client():
    return server.app.test_client()


@pytest.fixture
def state_path(tmp_path: Path) -> Path:
    return tmp_path / "state.json"


@pytest.fixture
def default_state():
    return storage.default_state()
