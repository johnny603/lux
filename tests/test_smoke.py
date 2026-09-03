import server


def test_import_server():
    assert server.app is not None


def test_health_endpoint():
    client = server.app.test_client()

    response = client.get("/health")

    assert response.status_code == 200

    response = client.get("/ready")
    assert response.status_code == 200


def test_levels_endpoint():
    client = server.app.test_client()

    response = client.get("/levels")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) > 0


def test_level_detail_and_submission_endpoints(monkeypatch):
    client = server.app.test_client()

    response = client.get("/level/1")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["id"] == "1"
    assert payload["difficulty"] == "easy"

    response = client.post("/submit", json={"level_id": "1", "attempt": "-a"})
    assert response.status_code == 200
    assert response.get_json()["correct"] is True

    response = client.post("/api/v1/submit", json={"level_id": "1", "attempt": "-a"})
    assert response.status_code == 200
    assert response.get_json()["correct"] is True

    monkeypatch.setattr(
        server, "run_docker", lambda files, script: {"passed": True, "exit_code": 0}
    )
    response = client.post(
        "/submit", json={"level_id": "5", "files": {"answer.c": "int main(void){return 0;}"}}
    )
    assert response.status_code == 200
    assert response.get_json()["correct"] is True


def test_invalid_submission_rejected():
    client = server.app.test_client()

    response = client.post("/submit", json={"level_id": "999", "attempt": "x"})
    assert response.status_code == 404
