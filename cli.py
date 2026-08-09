from typing import List, Dict, Set


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
        return (difficulty_key(l.get("difficulty")), l.get("id") or "")

    ordered = sorted(levels, key=key)
    # move solved to the end for discovery
    unsolved = [l for l in ordered if l.get("id") not in solved]
    solved_list = [l for l in ordered if l.get("id") in solved]
    return unsolved + solved_list


def format_level_line(level: Dict, solved: Set[str] = None) -> str:
    solved = solved or set()
    marker = "[x]" if level.get("id") in solved else "[ ]"
    tags = ", ".join(level.get("tags", []))
    return f"{marker} {level.get('id')}: {level.get('title')} ({level.get('difficulty','?')}) - {level.get('category','?')} {'- ' + tags if tags else ''}"
