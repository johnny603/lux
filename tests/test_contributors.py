import json

import pytest

import contributors
import server


def test_load_contributors_normalizes_entries(tmp_path):
    manifest = tmp_path / "contributors.json"
    manifest.write_text(
        json.dumps(
            {
                "contributors": [
                    {
                        "login": "ada",
                        "name": "Ada Lovelace",
                        "contributions": ["documentation"],
                        "badges": ["founding-contributor"],
                    },
                    {"name": "missing login"},
                ]
            }
        )
    )

    assert contributors.load_contributors(str(manifest)) == [
        {
            "login": "ada",
            "name": "Ada Lovelace",
            "contributions": ["documentation"],
            "badges": ["founding-contributor"],
        }
    ]


def test_load_contributors_handles_malformed_manifest(tmp_path):
    manifest = tmp_path / "contributors.json"
    manifest.write_text("not json")

    assert contributors.load_contributors(str(manifest)) == []
    assert contributors.load_contributors(str(tmp_path / "missing.json")) == []


def test_contributor_endpoints(monkeypatch):
    entries = [
        {
            "login": "ada",
            "name": "Ada Lovelace",
            "contributions": ["documentation"],
            "badges": ["founding-contributor"],
        }
    ]
    monkeypatch.setattr(server.contributors, "load_contributors", lambda: entries)
    client = server.app.test_client()

    response = client.get("/api/v1/contributors")
    assert response.status_code == 200
    assert response.get_json() == {"contributors": entries}

    response = client.get("/contributors")
    assert response.status_code == 200
    assert b"Ada Lovelace" in response.data
    assert b"founding-contributor" in response.data


@pytest.mark.parametrize("value", [None, 42, True, "documentation", {"kind": "code"}])
def test_load_contributors_ignores_non_list_contributions(tmp_path, value):
    manifest = tmp_path / "contributors.json"
    manifest.write_text(json.dumps({"contributors": [{"login": "ada", "contributions": value}]}))
    entries = contributors.load_contributors(str(manifest))
    assert len(entries) == 1
    assert entries[0]["login"] == "ada"
    assert entries[0]["contributions"] == []


@pytest.mark.parametrize("endpoint", ["/contributors", "/api/v1/contributors"])
def test_contributor_routes_handle_null_contributions(tmp_path, monkeypatch, endpoint):
    manifest = tmp_path / "contributors.json"
    manifest.write_text(json.dumps({"contributors": [{"login": "ada", "contributions": None}]}))
    load = contributors.load_contributors
    monkeypatch.setattr(server.contributors, "load_contributors", lambda: load(str(manifest)))
    response = server.app.test_client().get(endpoint)
    assert response.status_code == 200
    if endpoint.startswith("/api/"):
        assert response.get_json()["contributors"][0]["contributions"] == []
