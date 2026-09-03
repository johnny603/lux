import copy
import json
import os
import tempfile
from datetime import datetime, timezone

DEFAULT_STATE_ENV = "LUX_STATE"
STATE_VERSION = 2
RECENT_ACTIVITY_LIMIT = 50


def _utc_now():
    return datetime.now(timezone.utc)


def _iso_now():
    return _utc_now().isoformat()


def _parse_date(value):
    if not value:
        return None
    try:
        if isinstance(value, str) and value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value).astimezone(timezone.utc)
    except Exception:
        return None


def _date_key(value):
    parsed = _parse_date(value)
    return parsed.date().isoformat() if parsed else None


def _default_meta():
    return {
        "attempts_by_level": {},
        "history": [],
        "last_activity_at": None,
        "last_solved_at": None,
        "recent_solved": [],
        "total_attempts": 0,
        "total_solved": 0,
        "streak": {"current": 0, "longest": 0, "last_solved_date": None},
    }


def default_profile():
    now = _iso_now()
    return {
        "display_name": "Learner",
        "preferences": {
            "difficulty_preference": "any",
            "favorite_categories": [],
            "hint_style": "concise",
            "show_solved_first": False,
        },
        "created_at": now,
        "updated_at": now,
    }


def default_state():
    return {
        "version": STATE_VERSION,
        "solved": {},
        "achievements": {},
        "meta": _default_meta(),
        "profile": default_profile(),
        "game": _default_game(),
    }


def _default_game():
    return {
        "xp": 0,
        "level": 1,
        "daily": {"last_challenge_date": None, "completed_dates": []},
        "adventure": {"current_world": None, "unlocked_worlds": [], "campaign_progress": {}},
    }


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


def _normalize_solved_entry(entry, now=None):
    now = now or _iso_now()
    if not isinstance(entry, dict):
        entry = {}
    normalized = {
        "attempts": int(entry.get("attempts", 0) or 0),
        "first_solved": entry.get("first_solved") or now,
        "last_solved": entry.get("last_solved") or entry.get("first_solved") or now,
    }
    for key in ("title", "category", "difficulty", "tags"):
        if key in entry:
            normalized[key] = entry[key]
    return normalized


def _normalize_activity_entry(entry):
    if not isinstance(entry, dict):
        return None
    level_id = str(entry.get("level_id") or "").strip()
    if not level_id:
        return None
    return {
        "at": entry.get("at") or _iso_now(),
        "correct": bool(entry.get("correct", False)),
        "level_id": level_id,
        "title": entry.get("title"),
        "difficulty": entry.get("difficulty"),
        "category": entry.get("category"),
        "attempt_preview": entry.get("attempt_preview"),
    }


def normalize_state(state):
    if not isinstance(state, dict):
        return default_state()

    normalized = copy.deepcopy(state)
    normalized.setdefault("version", STATE_VERSION)
    if normalized["version"] < STATE_VERSION:
        normalized["version"] = STATE_VERSION

    solved = normalized.get("solved", {})
    if isinstance(solved, list):
        solved = {str(level_id): {} for level_id in solved}
    elif not isinstance(solved, dict):
        solved = {}
    normalized["solved"] = {
        str(level_id): _normalize_solved_entry(entry) for level_id, entry in solved.items()
    }

    achievements = normalized.get("achievements", {})
    normalized["achievements"] = achievements if isinstance(achievements, dict) else {}

    profile = normalized.get("profile", {})
    if not isinstance(profile, dict):
        profile = {}
    defaults = default_profile()
    merged_profile = {**defaults, **profile}
    prefs = profile.get("preferences", {})
    if not isinstance(prefs, dict):
        prefs = {}
    merged_profile["preferences"] = {**defaults["preferences"], **prefs}
    merged_profile.setdefault("created_at", defaults["created_at"])
    merged_profile.setdefault("updated_at", defaults["updated_at"])
    normalized["profile"] = merged_profile

    game = normalized.get("game", {})
    if not isinstance(game, dict):
        game = {}
    game_defaults = _default_game()
    merged_game = {**game_defaults, **game}
    daily = game.get("daily", {})
    if not isinstance(daily, dict):
        daily = {}
    merged_game["daily"] = {**game_defaults["daily"], **daily}
    adventure = game.get("adventure", {})
    if not isinstance(adventure, dict):
        adventure = {}
    merged_game["adventure"] = {**game_defaults["adventure"], **adventure}
    normalized["game"] = merged_game

    meta = normalized.get("meta", {})
    meta = meta if isinstance(meta, dict) else {}
    defaults = _default_meta()
    for key, value in defaults.items():
        meta.setdefault(key, copy.deepcopy(value))

    if not isinstance(meta.get("attempts_by_level"), dict):
        meta["attempts_by_level"] = {}
    if not isinstance(meta.get("history"), list):
        meta["history"] = []
    if not isinstance(meta.get("recent_solved"), list):
        meta["recent_solved"] = []

    meta["history"] = [
        item
        for item in (_normalize_activity_entry(entry) for entry in meta["history"])
        if item is not None
    ][-RECENT_ACTIVITY_LIMIT:]

    streak = meta.get("streak", {})
    if not isinstance(streak, dict):
        streak = {}
    meta["streak"] = {
        "current": int(streak.get("current", 0) or 0),
        "longest": int(streak.get("longest", 0) or 0),
        "last_solved_date": streak.get("last_solved_date"),
    }

    meta["total_attempts"] = int(meta.get("total_attempts", 0) or 0)
    meta["total_solved"] = int(meta.get("total_solved", len(normalized["solved"])) or 0)
    meta["last_activity_at"] = meta.get("last_activity_at")
    meta["last_solved_at"] = meta.get("last_solved_at")

    normalized["meta"] = meta
    return normalized


def load_state(path: str = None):
    path = path or default_state_path()
    if not os.path.exists(path):
        return default_state()
    try:
        with open(path, "r") as f:
            return normalize_state(json.load(f))
    except Exception:
        return default_state()


def save_state(state: dict, path: str = None):
    path = path or default_state_path()
    dirpath = os.path.dirname(path)
    os.makedirs(dirpath, exist_ok=True)
    normalized = normalize_state(state)
    fd, tmp = tempfile.mkstemp(dir=dirpath)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(normalized, f, indent=2, sort_keys=True)
        os.replace(tmp, path)
    finally:
        try:
            if os.path.exists(tmp):
                os.unlink(tmp)
        except Exception:
            pass


def record_attempt(
    state: dict,
    level_id: str,
    *,
    correct: bool = False,
    title: str = None,
    difficulty: str = None,
    category: str = None,
    attempt_preview: str = None,
    at: str = None,
):
    normalized = normalize_state(state)
    now = at or _iso_now()
    level_id = str(level_id)

    meta = normalized["meta"]
    meta["total_attempts"] += 1
    meta["last_activity_at"] = now

    attempts = meta.setdefault("attempts_by_level", {})
    entry = attempts.get(level_id, {})
    entry["attempts"] = int(entry.get("attempts", 0) or 0) + 1
    if not correct:
        entry["incorrect"] = int(entry.get("incorrect", 0) or 0) + 1
    entry["last_attempt_at"] = now
    entry["last_outcome"] = "correct" if correct else "incorrect"
    if title is not None:
        entry["title"] = title
    if difficulty is not None:
        entry["difficulty"] = difficulty
    if category is not None:
        entry["category"] = category
    if attempt_preview:
        entry["attempt_preview"] = attempt_preview[:120]
    attempts[level_id] = entry

    history = meta.setdefault("history", [])
    history.append(
        _normalize_activity_entry(
            {
                "at": now,
                "correct": correct,
                "level_id": level_id,
                "title": title,
                "difficulty": difficulty,
                "category": category,
                "attempt_preview": attempt_preview[:120] if attempt_preview else None,
            }
        )
    )
    meta["history"] = [item for item in history if item is not None][-RECENT_ACTIVITY_LIMIT:]
    state.update(normalized)
    return state


def _update_streak(meta: dict, solved_at: str):
    solved_date = _date_key(solved_at)
    if not solved_date:
        return
    streak = meta.setdefault("streak", {"current": 0, "longest": 0, "last_solved_date": None})
    last = streak.get("last_solved_date")
    last_date = _parse_date(last).date() if _parse_date(last) else None
    current_date = _parse_date(solved_date).date() if _parse_date(solved_date) else None

    current_streak = int(streak.get("current", 0) or 0)
    if last_date is None or current_date is None:
        streak["current"] = 1
    else:
        delta = (current_date - last_date).days
        if delta == 1:
            streak["current"] = current_streak + 1
        elif delta != 0:
            streak["current"] = 1
    streak["longest"] = max(int(streak.get("longest", 0) or 0), int(streak.get("current", 0) or 0))
    streak["last_solved_date"] = solved_date


def mark_solved(
    state: dict,
    level_id: str,
    attempts: int = 1,
    *,
    title: str = None,
    difficulty: str = None,
    category: str = None,
    at: str = None,
):
    normalized = normalize_state(state)
    solved = normalized.setdefault("solved", {})
    now = at or _iso_now()
    level_id = str(level_id)

    entry = _normalize_solved_entry(solved.get(level_id, {}), now=now)
    entry.setdefault("first_solved", now)
    entry["last_solved"] = now
    if attempts:
        entry["attempts"] = max(int(entry.get("attempts", 0) or 0), int(attempts))
    if title is not None:
        entry["title"] = title
    if difficulty is not None:
        entry["difficulty"] = difficulty
    if category is not None:
        entry["category"] = category
    solved_first_time = level_id not in solved
    solved[level_id] = entry

    meta = normalized.setdefault("meta", _default_meta())
    meta["last_activity_at"] = now
    meta["last_solved_at"] = now
    if solved_first_time:
        meta["total_solved"] = int(meta.get("total_solved", 0) or 0) + 1
        recent = [level_id] + [item for item in meta.get("recent_solved", []) if item != level_id]
        meta["recent_solved"] = recent[:10]
    else:
        meta.setdefault("recent_solved", [])
        if level_id not in meta["recent_solved"]:
            meta["recent_solved"] = [level_id] + meta["recent_solved"]
            meta["recent_solved"] = meta["recent_solved"][:10]
    _update_streak(meta, now)
    state.update(normalized)
    return state


def get_solved_levels(state: dict):
    return set(normalize_state(state).get("solved", {}).keys())


def get_level_attempt_stats(state: dict, level_id: str):
    normalized = normalize_state(state)
    return normalized.get("meta", {}).get("attempts_by_level", {}).get(str(level_id), {})


def get_profile(state: dict):
    return normalize_state(state).get("profile", default_profile())


def update_profile(state: dict, *, display_name=None, preferences=None):
    normalized = normalize_state(state)
    profile = normalized.setdefault("profile", default_profile())
    if display_name is not None:
        profile["display_name"] = str(display_name).strip() or profile.get(
            "display_name", "Learner"
        )
    if preferences is not None and isinstance(preferences, dict):
        prefs = profile.setdefault("preferences", {})
        prefs.update(preferences)
    profile["updated_at"] = _iso_now()
    state.update(normalized)
    return profile


def get_game_state(state: dict):
    return normalize_state(state).get("game", _default_game())


def award_xp(state: dict, amount: int):
    normalized = normalize_state(state)
    game = normalized.setdefault("game", _default_game())
    game["xp"] = int(game.get("xp", 0) or 0) + max(0, int(amount))
    while game["xp"] >= _xp_for_level(game["level"] + 1):
        game["level"] = int(game.get("level", 1) or 1) + 1
    state.update(normalized)
    return game


def _xp_for_level(level: int):
    return max(1, level) * 100


def get_progress_summary(state: dict, levels=None):
    normalized = normalize_state(state)
    solved = normalized.get("solved", {})
    meta = normalized.get("meta", {})
    total_levels = len(levels) if levels is not None else None
    solved_count = len(solved)
    percent = None
    if total_levels:
        percent = round((solved_count / total_levels) * 100, 1)
    return {
        "solved_count": solved_count,
        "total_levels": total_levels,
        "percent_complete": percent,
        "total_attempts": meta.get("total_attempts", 0),
        "current_streak": meta.get("streak", {}).get("current", 0),
        "longest_streak": meta.get("streak", {}).get("longest", 0),
        "recent_solved": meta.get("recent_solved", [])[:5],
        "last_solved_at": meta.get("last_solved_at"),
    }
