import json

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
