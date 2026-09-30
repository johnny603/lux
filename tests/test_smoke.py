import server


def test_import_server():
    assert server.app is not None


def test_health_endpoint(app_client):
    response = app_client.get("/health")

    assert response.status_code == 200

    response = app_client.get("/ready")
    assert response.status_code == 200


def test_levels_endpoint(app_client):
    response = app_client.get("/levels")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) > 0


def test_level_detail_and_submission_endpoints(monkeypatch, app_client):
    response = app_client.get("/level/1")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["id"] == "1"
    assert payload["difficulty"] == "easy"

    response = app_client.post("/submit", json={"level_id": "1", "attempt": "-a"})
    assert response.status_code == 200
    assert response.get_json()["correct"] is True

    response = app_client.post("/api/v1/submit", json={"level_id": "1", "attempt": "-a"})
    assert response.status_code == 200
    assert response.get_json()["correct"] is True

    monkeypatch.setattr(
        server, "run_docker", lambda files, script: {"passed": True, "exit_code": 0}
    )
    response = app_client.post(
        "/submit", json={"level_id": "5", "files": {"answer.c": "int main(void){return 0;}"}}
    )
    assert response.status_code == 200
    assert response.get_json()["correct"] is True


def test_invalid_submission_rejected(app_client):
    response = app_client.post("/submit", json={"level_id": "999", "attempt": "x"})
    assert response.status_code == 404
