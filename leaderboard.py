from __future__ import annotations

from typing import Dict, List, Optional


def _safe_profile_name(state: Dict) -> str:
    profile = state.get("profile") or {}
    name = profile.get("display_name") or "Learner"
    return str(name).strip() or "Learner"


def _score_for_entry(state: Dict, entry: Dict, metric: str) -> float:
    if metric == "streak":
        return float(entry.get("streak", 0) or 0)
    if metric == "xp":
        return float(entry.get("xp", 0) or 0)
    return float(entry.get("solved_count", 0) or 0)


def get_leaderboard(state: Dict, levels: Optional[List[Dict]] = None, metric: str = "solved_count") -> Dict:
    profile_name = _safe_profile_name(state)
    solved = state.get("solved") or {}
    streak = (state.get("meta") or {}).get("streak") or {}
    game = (state.get("game") or {})
    entry = {
        "name": profile_name,
        "solved_count": len(solved),
        "streak": int(streak.get("current", 0) or 0),
        "xp": int(game.get("xp", 0) or 0),
    }
    return {
        "metric": metric,
        "entries": [
            {
                "name": entry["name"],
                "solved_count": entry["solved_count"],
                "streak": entry["streak"],
                "xp": entry["xp"],
                "score": _score_for_entry(state, entry, metric),
            }
        ],
    }


def upsert_local_entry(state: Dict, levels: Optional[List[Dict]] = None) -> Dict:
    board = state.setdefault("leaderboard", {})
    board["local"] = {
        "name": _safe_profile_name(state),
        "solved_count": len(state.get("solved") or {}),
        "streak": int((state.get("meta") or {}).get("streak", {}).get("current", 0) or 0),
        "xp": int((state.get("game") or {}).get("xp", 0) or 0),
    }
    return board
