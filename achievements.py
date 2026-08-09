from datetime import datetime, timezone
from typing import Dict, List, Optional


ACHIEVEMENTS = [
    {"id": "first_solve", "title": "First Solve", "description": "Solve your first puzzle."},
    {"id": "solve_5", "title": "Solver: 5", "description": "Solve 5 puzzles."},
    {"id": "solve_10", "title": "Solver: 10", "description": "Solve 10 puzzles."},
    {"id": "solve_25", "title": "Solver: 25", "description": "Solve 25 puzzles."},
]


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _ach_by_id(aid: str):
    for a in ACHIEVEMENTS:
        if a["id"] == aid:
            return a
    return None


def evaluate_achievements(state: Dict, levels: Optional[List[Dict]] = None) -> List[Dict]:
    """Evaluate achievements based on current state and optional levels metadata.

    Returns a list of newly unlocked achievement dicts.
    """
    unlocked = state.setdefault("achievements", {})
    solved = set(state.get("solved", {}).keys())
    newly = []

    # simple count-based achievements
    n = len(solved)
    thresholds = [
        ("first_solve", n >= 1),
        ("solve_5", n >= 5),
        ("solve_10", n >= 10),
        ("solve_25", n >= 25),
    ]
    for aid, cond in thresholds:
        if cond and aid not in unlocked:
            meta = _ach_by_id(aid) or {"id": aid}
            unlocked[aid] = {"unlocked_at": _now_iso(), "title": meta.get("title"), "description": meta.get("description")}
            newly.append({"id": aid, **unlocked[aid]})

    # category completion achievements if levels provided
    if levels:
        # build category -> set(ids)
        cats = {}
        for l in levels:
            cid = l.get("category") or "uncategorized"
            cats.setdefault(cid, set()).add(l.get("id"))
        for cat, ids in cats.items():
            if ids and ids.issubset(solved) and f"category_{cat}" not in unlocked:
                aid = f"category_{cat}"
                unlocked[aid] = {"unlocked_at": _now_iso(), "title": f"Master: {cat}", "description": f"Solve all puzzles in {cat}."}
                newly.append({"id": aid, **unlocked[aid]})

    return newly
