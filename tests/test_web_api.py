import re
from io import BytesIO

import server


def test_web_browser_and_dashboard_render():
    client = server.app.test_client()

    response = client.get("/web")
    assert response.status_code == 200
    assert b"Puzzle Browser" in response.data

    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"Progress Dashboard" in response.data

    response = client.get("/profile")
    assert response.status_code == 200
    assert b"User Profile" in response.data

    response = client.get("/leaderboard")
    assert response.status_code == 200
    assert b"Leaderboard" in response.data


def test_versioned_api_endpoints():
    client = server.app.test_client()

    response = client.get("/api/v1/levels")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

    response = client.get("/api/v1/level/1")
    assert response.status_code == 200
    assert response.get_json()["id"] == "1"

    response = client.get("/api/v1/progress")
    assert response.status_code == 200
    payload = response.get_json()
    assert "progress" in payload
    assert "achievements" in payload

    response = client.get("/api/v1/profile")
    assert response.status_code == 200
    assert "display_name" in response.get_json()

    response = client.get("/api/v1/leaderboard")
    assert response.status_code == 200
    assert "entries" in response.get_json()

    response = client.get("/api/v1/learning-path")
    assert response.status_code == 200
    assert "recommended_levels" in response.get_json()

    response = client.get("/api/v1/game/daily")
    assert response.status_code == 200
    assert "level" in response.get_json()


def test_web_submission_flow(monkeypatch):
    client = server.app.test_client()
    monkeypatch.setattr(
        server, "run_docker", lambda files, script: {"passed": True, "exit_code": 0}
    )

    page = client.get("/puzzles/5")
    assert page.status_code == 200
    token_match = re.search(r'name="csrf_token" value="([^"]+)"', page.get_data(as_text=True))
    assert token_match is not None

    response = client.post(
        "/puzzles/5/submit",
        data={
            "csrf_token": token_match.group(1),
            "answer": "",
            "files": (BytesIO(b"int main(void){return 0;}"), "answer.c"),
        },
    )
    assert response.status_code == 200
    assert b"Submission accepted" in response.data


def test_api_documentation_contract_and_errors():
    client = server.app.test_client()

    # Health and ready
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.get_json()["ok"] is True

    res_ready = client.get("/ready")
    assert res_ready.status_code == 200
    assert res_ready.get_json()["ok"] is True

    # 404 for non-existent level
    res_not_found = client.get("/api/v1/level/99999")
    assert res_not_found.status_code == 404
    assert res_not_found.get_json()["ok"] is False
    assert res_not_found.get_json()["error"] == "not found"

    # Submission error responses
    res_missing_id = client.post("/api/v1/submit", json={"attempt": "test"})
    assert res_missing_id.status_code == 400
    assert res_missing_id.get_json()["ok"] is False
    assert res_missing_id.get_json()["error"] == "missing level_id"

    res_invalid_lvl = client.post("/api/v1/submit", json={"level_id": "99999", "attempt": "test"})
    assert res_invalid_lvl.status_code == 404
    assert res_invalid_lvl.get_json()["ok"] is False
    assert res_invalid_lvl.get_json()["error"] == "invalid level"
