import server


def test_import_server():
    assert server.app is not None


def test_health_endpoint():
    client = server.app.test_client()

    response = client.get("/health")

    assert response.status_code == 200


def test_levels_endpoint():
    client = server.app.test_client()

    response = client.get("/levels")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) > 0
