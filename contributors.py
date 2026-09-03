import json
import os
from typing import Any, Dict, List


DEFAULT_MANIFEST = os.path.join(os.path.dirname(__file__), "contributors.json")


def load_contributors(path: str = DEFAULT_MANIFEST) -> List[Dict[str, Any]]:
    """Load a contributor manifest, returning an empty list for bad optional data."""
    try:
        with open(path, encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, TypeError, ValueError):
        return []

    entries = payload.get("contributors", []) if isinstance(payload, dict) else []
    if not isinstance(entries, list):
        return []

    valid = []
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("login"):
            continue
        badges = entry.get("badges", [])
        valid.append({
            "login": str(entry["login"]),
            "name": str(entry.get("name") or entry["login"]),
            "contributions": [str(item) for item in entry.get("contributions", []) if item],
            "badges": [str(item) for item in badges if item] if isinstance(badges, list) else [],
        })
    return valid
