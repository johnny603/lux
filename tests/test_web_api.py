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


def test_web_submission_flow(monkeypatch):
    client = server.app.test_client()
    monkeypatch.setattr(server, "run_docker", lambda files, script: {"passed": True, "exit_code": 0})

    page = client.get("/puzzles/5")
    assert page.status_code == 200
    token_match = re.search(r'name="csrf_token" value="([^"]+)"', page.get_data(as_text=True))
    assert token_match is not None

    response = client.post(
        "/puzzles/5/submit",
        data={"csrf_token": token_match.group(1), "answer": "", "files": (BytesIO(b"int main(void){return 0;}"), "answer.c")},
    )
    assert response.status_code == 200
    assert b"Submission accepted" in response.data
