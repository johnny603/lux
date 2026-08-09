from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional

import storage


def on_level_solved(state: Dict, level: Optional[Dict] = None) -> Dict:
    state = storage.normalize_state(state)
    game = state.setdefault("game", storage._default_game())
    difficulty = (level or {}).get("difficulty") or "easy"
    xp_gain = {"easy": 25, "medium": 50, "hard": 75}.get(difficulty.lower(), 25)
    storage.award_xp(state, xp_gain)

    today = date.today().isoformat()
    daily = game.setdefault("daily", {"last_challenge_date": None, "completed_dates": []})
    completed = daily.setdefault("completed_dates", [])
    if today not in completed:
        completed.append(today)
        daily["last_challenge_date"] = today
    return storage.normalize_state(state)


def daily_challenge_status(state: Dict, levels: Optional[List[Dict]] = None) -> Dict:
    state = storage.normalize_state(state)
    levels = levels or []
    today = date.today().isoformat()
    daily = (state.get("game") or {}).get("daily") or {}
    completed_today = today in (daily.get("completed_dates") or [])
    level = None
    if levels:
        solved = set(state.get("solved", {}).keys())
        level = next((lvl for lvl in levels if str(lvl.get("id")) not in solved), None)
    if level is None and levels:
        level = levels[0]
    return {
        "date": today,
        "completed_today": completed_today,
        "level": {
            "id": level.get("id") if level else None,
            "title": level.get("title") if level else None,
            "category": level.get("category") if level else None,
            "difficulty": level.get("difficulty") if level else None,
        },
    }


def adventure_status(state: Dict, levels: Optional[List[Dict]] = None) -> Dict:
    state = storage.normalize_state(state)
    adventure = (state.get("game") or {}).get("adventure") or {}
    return {
        "current_world": adventure.get("current_world"),
        "unlocked_worlds": adventure.get("unlocked_worlds", []),
        "campaign_progress": adventure.get("campaign_progress", {}),
        "xp": int((state.get("game") or {}).get("xp", 0) or 0),
    }
