from __future__ import annotations

from typing import Dict, List, Optional


def build_learning_path(state: Dict, levels: Optional[List[Dict]] = None, limit: int = 5) -> Dict:
    levels = levels or []
    solved = set(state.get("solved", {}).keys())
    unsolved = [lvl for lvl in levels if str(lvl.get("id")) not in solved]
    if not unsolved:
        return {
            "summary": "You have completed the available puzzles.",
            "recommended_levels": [],
            "limit": limit,
        }

    ordered = sorted(
        unsolved,
        key=lambda lvl: (
            (lvl.get("difficulty") or "").lower() != "easy",
            (lvl.get("difficulty") or "").lower() not in {"easy", "medium"},
            (lvl.get("category") or "").lower(),
            (lvl.get("title") or "").lower(),
        ),
    )
    recommended = ordered[: max(1, int(limit))]
    summary = (
        f"Focus on {len(recommended)} next steps that balance difficulty and your recent progress."
    )
    return {
        "summary": summary,
        "recommended_levels": [
            {
                "id": lvl.get("id"),
                "title": lvl.get("title"),
                "category": lvl.get("category"),
                "difficulty": lvl.get("difficulty"),
            }
            for lvl in recommended
        ],
        "limit": limit,
    }
