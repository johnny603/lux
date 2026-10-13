from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional

# Default room catalog demonstrating progressive escape-room structure
DEFAULT_ROOMS: List[Dict[str, Any]] = [
    {
        "id": "room-1",
        "name": "The Antechamber",
        "description": (
            "A dimly lit room with flickering monitors. "
            "The door is sealed by a basic terminal lock."
        ),
        "difficulty": 1,
        "required_previous_room": None,
        "hints": [
            "Inspect the filesystem carefully for hidden clues.",
            "Hidden files in Unix usually start with a dot.",
        ],
        "escape_condition": {
            "puzzle_id": "1",
            "type": "puzzle_solved",
            "description": "Unlock the terminal by finding the hidden files parameter.",
        },
    },
    {
        "id": "room-2",
        "name": "The Compiler Laboratory",
        "description": (
            "Shelves of punch cards and C code listings line the walls. "
            "A build pipeline must execute cleanly."
        ),
        "difficulty": 2,
        "required_previous_room": "room-1",
        "hints": [
            "Use the standard GCC compiler syntax.",
            "Make sure to specify the output binary filename.",
        ],
        "escape_condition": {
            "puzzle_id": "2",
            "type": "puzzle_solved",
            "description": "Compile the hello executable to power the lab door.",
        },
    },
    {
        "id": "room-3",
        "name": "The Storage Archive",
        "description": (
            "Gigantic disk arrays hum in the dark. "
            "Large storage files are blocking the ventilation shaft."
        ),
        "difficulty": 2,
        "required_previous_room": "room-2",
        "hints": [
            "The find command can filter files by size.",
            "Look for files exceeding 1 Megabyte.",
        ],
        "escape_condition": {
            "puzzle_id": "3",
            "type": "puzzle_solved",
            "description": "Locate files over 1MB to clear the archive passage.",
        },
    },
    {
        "id": "room-4",
        "name": "The Access Gate",
        "description": (
            "A heavy blast door with strict permission controls "
            "requires precise security octal modes."
        ),
        "difficulty": 3,
        "required_previous_room": "room-3",
        "hints": [
            "Permissions are calculated in octal: read is 4, write is 2, execute is 1.",
            "Owner read-write is 6, group read is 4, others read is 4.",
        ],
        "escape_condition": {
            "puzzle_id": "4",
            "type": "puzzle_solved",
            "description": "Set proper rw-r--r-- permissions on the gate key.",
        },
    },
    {
        "id": "room-5",
        "name": "The Central Core",
        "description": (
            "The heart of the facility. "
            "You need to provide the ultimate answer to escape to freedom."
        ),
        "difficulty": 4,
        "required_previous_room": "room-4",
        "hints": [
            "Write a C program that outputs the ultimate answer.",
            "Standard printf with number 42.",
        ],
        "escape_condition": {
            "puzzle_id": "5",
            "type": "puzzle_solved",
            "description": "Execute the 42 program in the sandbox to complete the escape.",
        },
    },
]


def get_all_rooms() -> List[Dict[str, Any]]:
    """Return a deep copy of all configured rooms."""
    return copy.deepcopy(DEFAULT_ROOMS)


def get_room(room_id: str) -> Optional[Dict[str, Any]]:
    """Return a room by its ID, or None if not found."""
    for room in DEFAULT_ROOMS:
        if room["id"] == str(room_id):
            return copy.deepcopy(room)
    return None


def is_room_unlocked(room: Dict[str, Any], escaped_rooms: set[str] | list[str]) -> bool:
    """Determine whether a room is unlocked based on escaped prerequisite rooms."""
    req = room.get("required_previous_room")
    if not req:
        return True
    return req in set(escaped_rooms)


def decorate_room(room: Dict[str, Any], escaped_rooms: set[str] | list[str]) -> Dict[str, Any]:
    """Decorate a room dict with dynamic status and lock flags."""
    escaped_set = set(escaped_rooms)
    r = copy.deepcopy(room)
    is_escaped = r["id"] in escaped_set
    unlocked = is_room_unlocked(r, escaped_set)
    
    if is_escaped:
        status = "escaped"
    elif unlocked:
        status = "unlocked"
    else:
        status = "locked"

    r["is_unlocked"] = unlocked
    r["is_escaped"] = is_escaped
    r["status"] = status
    return r


def get_rooms_summary(escaped_rooms: set[str] | list[str]) -> List[Dict[str, Any]]:
    """Return all rooms decorated with their current unlock/escape status."""
    return [decorate_room(room, escaped_rooms) for room in DEFAULT_ROOMS]
