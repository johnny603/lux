import os
import json
import tempfile
from datetime import datetime


DEFAULT_STATE_ENV = "LUX_STATE"


def default_state_path():
    path = os.getenv(DEFAULT_STATE_ENV)
    if path:
        return path
    home = os.path.expanduser("~")
    cfg_dir = os.path.join(home, ".lux")
    try:
        os.makedirs(cfg_dir, exist_ok=True)
    except Exception:
        pass
    return os.path.join(cfg_dir, "state.json")


def load_state(path: str = None):
    path = path or default_state_path()
    if not os.path.exists(path):
        return {"version": 1, "solved": {}, "meta": {}}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        # On any parse/read error, return fresh state to avoid crashing the CLI
        return {"version": 1, "solved": {}, "meta": {}}


def save_state(state: dict, path: str = None):
    path = path or default_state_path()
    dirpath = os.path.dirname(path)
    os.makedirs(dirpath, exist_ok=True)
    # atomic write
    fd, tmp = tempfile.mkstemp(dir=dirpath)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(state, f, indent=2, sort_keys=True)
        os.replace(tmp, path)
    finally:
        try:
            if os.path.exists(tmp):
                os.unlink(tmp)
        except Exception:
            pass


def mark_solved(state: dict, level_id: str, attempts: int = 1):
    solved = state.setdefault("solved", {})
    now = datetime.utcnow().isoformat() + "Z"
    entry = solved.get(level_id, {})
    entry.setdefault("first_solved", now)
    entry["last_solved"] = now
    entry["attempts"] = entry.get("attempts", 0) + attempts
    solved[level_id] = entry
    return state


def get_solved_levels(state: dict):
    return set(state.get("solved", {}).keys())
