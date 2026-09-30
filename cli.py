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

    def key(level):
        return (
            level.get("id") in solved,
            difficulty_key(level.get("difficulty")),
            (level.get("category") or "").lower(),
            (level.get("title") or "").lower(),
            level.get("id") or "",
        )

    ordered = sorted(levels, key=key)
    return ordered


def _level_matches_text(level: Dict, query: str) -> bool:
    haystack = " ".join(
        str(level.get(field, ""))
        for field in ("id", "title", "description", "category", "difficulty")
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
        f"({level.get('difficulty', '?')}) - {level.get('category', '?')}"
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
        f"streak {summary.get('current_streak', 0)} / best {summary.get('longest_streak', 0)}"
    )
    pieces.append(f"attempts {summary.get('total_attempts', 0)}")
    recent = summary.get("recent_solved") or []
    if recent:
        pieces.append("recent " + ", ".join(recent[:3]))
    return " | ".join(pieces)


def format_room_atmosphere(room: Dict) -> str:
    if not room:
        return "Chamber atmosphere details unavailable."
    rname = room.get("name", "Unknown Chamber")
    rid = room.get("id", "")
    theme = room.get("theme", "industrial-facility")
    atmosphere = room.get("atmosphere") or {}

    ambient = atmosphere.get("ambient_text", room.get("description", ""))
    sights = atmosphere.get("sights", "Minimal lighting with active console terminals.")
    sounds = atmosphere.get("sounds", "Faint mechanical hum and cooling fans.")
    smells = atmosphere.get("smells", "Static electricity and warm electronics.")
    ascii_art = atmosphere.get("ascii_art", "")

    lines = [
        f"🌌 === Atmosphere & Observation: {rname} [{rid}] ===",
        f"🏷️ Theme: {theme}",
        f"📖 Ambient: {ambient}",
        f"👁️ Sights: {sights}",
        f"👂 Sounds: {sounds}",
        f"👃 Smells: {smells}",
    ]
    if ascii_art:
        lines.append("\n🗺️ Room Map / Layout:")
        lines.append(ascii_art)

    objs = room.get("objects", [])
    if objs:
        lines.append("\n📦 Visible Interactive Items:")
        for obj in objs:
            take_tag = "[Takeable]" if obj.get("is_pickupable") else "[Fixed]"
            lines.append(
                f"  * {obj.get('name')} ({obj.get('id')}) {take_tag} - {obj.get('description')}"
            )

    return "\n".join(lines)


def format_room_objects(objects: Sequence[Dict]) -> str:
    if not objects:
        return "No interactive objects found in this chamber."
    lines = ["Chamber Objects:"]
    for obj in objects:
        pickup_tag = "[pickupable]" if obj.get("is_pickupable") else "[static]"
        lines.append(
            f"  * {obj.get('name', 'Unknown')} ({obj.get('id', '')}) {pickup_tag}: "
            f"{obj.get('description', '')}"
        )
    return "\n".join(lines)


def examine_object(obj: Dict) -> str:
    if not obj:
        return "Object not found."
    lines = [
        f"=== {obj.get('name')} ===",
        f"ID: {obj.get('id')}",
        f"Pickupable: {'Yes' if obj.get('is_pickupable') else 'No'}",
        f"Description: {obj.get('description')}",
    ]
    hint = obj.get("interaction_hint")
    if hint:
        lines.append(f"Hint: {hint}")
    triggers = obj.get("triggers", [])
    if triggers:
        lines.append("Actions:")
        for t in triggers:
            lines.append(f"  - [{t.get('action')}]: {t.get('message')}")
    return "\n".join(lines)


def format_inventory(inventory_items: Sequence[Dict]) -> str:
    if not inventory_items:
        return "Inventory is empty."
    lines = ["🎒 Player Inventory:"]
    for item in inventory_items:
        usable = ""
        if item.get("usable_on"):
            usable = f" (Usable on: {', '.join(item.get('usable_on', []))})"
        name = item.get("name", item.get("id", "Unknown"))
        oid = item.get("id", "")
        desc = item.get("description", "")
        lines.append(f"  * {name} [{oid}]{usable}: {desc}")
    return "\n".join(lines)


def format_room_timer(timer_info: Optional[Dict]) -> str:
    if not timer_info or not timer_info.get("time_limit_seconds"):
        return "No active countdown limit."
    limit = timer_info.get("time_limit_seconds")
    rem = timer_info.get("remaining_seconds", 0)
    if timer_info.get("is_expired"):
        return f"⏱️ TIME EXPIRED! ({limit}s limit exceeded. Reset room to retry)."
    return f"⏱️ {rem}s remaining (Time limit: {limit}s)"


def format_adaptive_hints(hints_data: Optional[Dict]) -> str:
    if not hints_data or not hints_data.get("hints"):
        return "No hints available for this chamber."
    rname = hints_data.get("room_name", "Room")
    unlocked_cnt = hints_data.get("unlocked_hints_count", 0)
    total_cnt = hints_data.get("total_hints_count", 0)
    failed = hints_data.get("failed_attempts", 0)
    header = (
        f"💡 Adaptive Hints for {rname} "
        f"({unlocked_cnt}/{total_cnt} unlocked | failed attempts: {failed}):"
    )
    lines = [header]
    for h in hints_data.get("hints", []):
        lvl = h.get("level", 1)
        lvl_tag = {1: "Subtle Clue", 2: "Directional Guidance", 3: "Direct Solution"}.get(
            lvl, f"Level {lvl}"
        )
        if h.get("is_unlocked"):
            lines.append(f"  [Level {lvl} - {lvl_tag}] ✅ {h.get('text')}")
        else:
            cond = h.get("unlock_condition")
            lines.append(f"  [Level {lvl} - {lvl_tag}] 🔒 {h.get('text')} (Unlock: {cond})")
    return "\n".join(lines)
