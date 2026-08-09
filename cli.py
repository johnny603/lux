from typing import Dict, List, Optional, Sequence, Set

import storage


def difficulty_key(d: str) -> int:
    # lower is easier
    if not d:
        return 99
    d = d.lower()
    if d == "easy":
        return 0
    if d == "medium":
        return 1
    if d == "hard":
        return 2
    return 99


def sort_levels(levels: List[Dict], solved: Set[str] = None) -> List[Dict]:
    solved = solved or set()

    def key(l):
        return (
            l.get("id") in solved,
            difficulty_key(l.get("difficulty")),
            (l.get("category") or "").lower(),
            (l.get("title") or "").lower(),
            l.get("id") or "",
        )

    ordered = sorted(levels, key=key)
    return ordered


def _level_matches_text(level: Dict, query: str) -> bool:
    haystack = " ".join(
        str(level.get(field, "")) for field in ("id", "title", "description", "category", "difficulty")
    ).lower()
    return query in haystack


def _level_matches_tags(level: Dict, tags: Optional[Set[str]]) -> bool:
    if not tags:
        return True
    level_tags = {tag.lower() for tag in level.get("tags", [])}
    return tags.issubset(level_tags)


def _level_matches_filters(
    level: Dict,
    *,
    category: Optional[str],
    difficulty: Optional[str],
    query: Optional[str],
    tag_set: Optional[Set[str]],
) -> bool:
    if category and (level.get("category") or "").lower() != category:
        return False
    if difficulty and (level.get("difficulty") or "").lower() != difficulty:
        return False
    if query and not _level_matches_text(level, query):
        return False
    return _level_matches_tags(level, tag_set)


def filter_levels(
    levels: Sequence[Dict],
    *,
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    query: Optional[str] = None,
    tags: Optional[Sequence[str]] = None,
) -> List[Dict]:
    category = category.lower().strip() if category else None
    difficulty = difficulty.lower().strip() if difficulty else None
    query = query.lower().strip() if query else None
    tag_set = {tag.lower().strip() for tag in tags} if tags else None

    return [
        level
        for level in levels
        if _level_matches_filters(
            level,
            category=category,
            difficulty=difficulty,
            query=query,
            tag_set=tag_set,
        )
    ]


def format_level_line(level: Dict, solved: Set[str] = None) -> str:
    solved = solved or set()
    marker = "[x]" if level.get("id") in solved else "[ ]"
    tags = ", ".join(level.get("tags", []))
    attempts = level.get("attempts")
    attempt_text = f" · attempts {attempts}" if attempts else ""
    return (
        f"{marker} {level.get('id')}: {level.get('title')} "
        f"({level.get('difficulty','?')}) - {level.get('category','?')}"
        f"{attempt_text}"
        f"{' - ' + tags if tags else ''}"
    )


def format_progress_summary(state: Dict, levels: Optional[List[Dict]] = None) -> str:
    summary = storage.get_progress_summary(state, levels)
    pieces = [f"Solved {summary['solved_count']}"]
    if summary.get("total_levels"):
        pieces.append(f"of {summary['total_levels']}")
    if summary.get("percent_complete") is not None:
        pieces.append(f"({summary['percent_complete']}%)")
    pieces.append(
        f"streak {summary.get('current_streak', 0)}"
        f" / best {summary.get('longest_streak', 0)}"
    )
    pieces.append(f"attempts {summary.get('total_attempts', 0)}")
    recent = summary.get("recent_solved") or []
    if recent:
        pieces.append("recent " + ", ".join(recent[:3]))
    return " | ".join(pieces)
