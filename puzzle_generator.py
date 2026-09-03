from __future__ import annotations

from typing import Dict, Iterable, Optional


def _validate_generated_puzzle(puzzle: Dict) -> bool:
    if not isinstance(puzzle, dict):
        return False
    required = {"id", "title", "description", "hint", "validator"}
    if not required.issubset(puzzle):
        return False
    if puzzle.get("validator") == "script" and not puzzle.get("test_script"):
        return False
    if puzzle.get("validator") not in {"equals", "contains", "script"}:
        return False
    return True


def generate_puzzle_with_ai(
    *,
    category: str,
    difficulty: str,
    topic: str,
    existing_ids: Iterable[str],
    next_id: Optional[str] = None,
) -> Dict:
    category = (category or "Programming").strip() or "Programming"
    difficulty = (difficulty or "easy").strip().lower() or "easy"
    topic = (topic or "practice").strip() or "practice"
    next_id = next_id or "999"
    puzzle = {
        "id": next_id,
        "title": f"{category}: {topic.title()}",
        "description": f"Create a short solution for the {topic} challenge.",
        "hint": f"Think about the {difficulty} concept for {topic}.",
        "validator": "equals",
        "flag": "sample-output",
        "category": category,
        "difficulty": difficulty,
        "tags": [category.lower(), topic.lower(), difficulty],
    }
    if puzzle["id"] in set(existing_ids or []):
        puzzle["id"] = str(int(next_id) + 1)
    if not _validate_generated_puzzle(puzzle):
        raise ValueError("Generated puzzle failed validation")
    return puzzle
