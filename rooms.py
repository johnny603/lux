from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional

# Default room catalog with interactive objects, triggers, hints, and progression
DEFAULT_ROOMS: List[Dict[str, Any]] = [
    {
        "id": "room-1",
        "name": "The Antechamber",
        "description": (
            "A dimly lit room with flickering monitors. "
            "The door is sealed by a basic terminal lock."
        ),
        "difficulty": 1,
        "time_limit_seconds": None,
        "locked": False,
        "required_previous_room": None,
        "unlock_condition": {
            "type": "starter",
            "description": "Initial unlocked entry point to the facility.",
        },
        "hints": [
            "Inspect the filesystem carefully for hidden clues.",
            "Hidden files in Unix usually start with a dot.",
        ],
        "escape_condition": {
            "puzzle_id": "1",
            "type": "puzzle_solved",
            "description": "Unlock the terminal by finding the hidden files parameter.",
        },
        "objects": [
            {
                "id": "obj-flickering-terminal",
                "name": "Flickering Terminal",
                "description": "A CRT monitor glowing green with bash commands scrolling by.",
                "is_pickupable": False,
                "interaction_hint": "Type 'examine terminal' or click to read system logs.",
                "triggers": [
                    {
                        "action": "examine",
                        "message": (
                            "System Log: Welcome to Lux Facility. "
                            "Hidden files parameter key initialized in root directory."
                        ),
                        "state_effect": "terminal_inspected",
                    }
                ],
            },
            {
                "id": "obj-brass-keycard",
                "name": "Brass Keycard",
                "description": "An old magnetic keycard covered in dust.",
                "is_pickupable": True,
                "interaction_hint": "Pick up the keycard for secure room access.",
                "triggers": [
                    {
                        "action": "pickup",
                        "message": "You picked up the Brass Keycard with intact magnetic stripe.",
                        "state_effect": "has_brass_keycard",
                    }
                ],
            },
            {
                "id": "obj-fuse-box",
                "name": "Auxiliary Fuse Box",
                "description": "A metal wall box with warning hazard stripes.",
                "is_pickupable": False,
                "interaction_hint": "Open and inspect the circuit switches.",
                "triggers": [
                    {
                        "action": "interact",
                        "message": "You flip the backup breaker. Lighting stabilizes in the room.",
                        "state_effect": "power_stabilized",
                    }
                ],
            },
        ],
    },
    {
        "id": "room-2",
        "name": "The Compiler Laboratory",
        "description": (
            "Shelves of punch cards and C code listings line the walls. "
            "A build pipeline must execute cleanly."
        ),
        "difficulty": 2,
        "time_limit_seconds": 300,
        "locked": True,
        "required_previous_room": "room-1",
        "unlock_condition": {
            "type": "room_escaped",
            "room_id": "room-1",
            "description": "Escape room-1 (The Antechamber) to unlock.",
        },
        "hints": [
            "Use the standard GCC compiler syntax.",
            "Make sure to specify the output binary filename.",
        ],
        "escape_condition": {
            "puzzle_id": "2",
            "type": "puzzle_solved",
            "description": "Compile the hello executable to power the lab door.",
        },
        "objects": [
            {
                "id": "obj-compiler-workbench",
                "name": "Mainframe Workstation",
                "description": "A rugged terminal hooked into a C compilation toolchain.",
                "is_pickupable": False,
                "interaction_hint": "Check the compiler flags and standard library headers.",
                "triggers": [
                    {
                        "action": "examine",
                        "message": (
                            "Toolchain status: gcc 13.2.0 ready. "
                            "Target: hello.c -> hello binary."
                        ),
                        "state_effect": "workbench_ready",
                    }
                ],
            },
            {
                "id": "obj-c-reference-manual",
                "name": "K&R C Reference Guide",
                "description": "A dog-eared copy of the classic C programming handbook.",
                "is_pickupable": True,
                "interaction_hint": "Take the manual with you for syntax lookup.",
                "triggers": [
                    {
                        "action": "pickup",
                        "message": "Added K&R C Reference Guide to your knowledge tools.",
                        "state_effect": "has_c_manual",
                    }
                ],
            },
        ],
    },
    {
        "id": "room-3",
        "name": "The Storage Archive",
        "description": (
            "Gigantic disk arrays hum in the dark. "
            "Large storage files are blocking the ventilation shaft."
        ),
        "difficulty": 2,
        "time_limit_seconds": 240,
        "locked": True,
        "required_previous_room": "room-2",
        "unlock_condition": {
            "type": "room_escaped",
            "room_id": "room-2",
            "description": "Escape room-2 (The Compiler Laboratory) to unlock.",
        },
        "hints": [
            "The find command can filter files by size.",
            "Look for files exceeding 1 Megabyte.",
        ],
        "escape_condition": {
            "puzzle_id": "3",
            "type": "puzzle_solved",
            "description": "Locate files over 1MB to clear the archive passage.",
        },
        "objects": [
            {
                "id": "obj-storage-rack",
                "name": "Magnetic Tape Rack",
                "description": "Rows of high-density tape cartridges indexing system snapshots.",
                "is_pickupable": False,
                "interaction_hint": "Scan through sector indices.",
                "triggers": [
                    {
                        "action": "examine",
                        "message": (
                            "Sector Index: Multiple large dumps found in /archive "
                            "spanning >1MB."
                        ),
                        "state_effect": "tape_indices_found",
                    }
                ],
            },
            {
                "id": "obj-scanner-tool",
                "name": "Handheld Byte Scanner",
                "description": "A digital tool used to verify block device sector sizes.",
                "is_pickupable": True,
                "interaction_hint": "Pick up the byte scanner.",
                "triggers": [
                    {
                        "action": "pickup",
                        "message": "Acquired Handheld Byte Scanner.",
                        "state_effect": "has_byte_scanner",
                    }
                ],
            },
        ],
    },
    {
        "id": "room-4",
        "name": "The Access Gate",
        "description": (
            "A heavy blast door with strict permission controls "
            "requires precise security octal modes."
        ),
        "difficulty": 3,
        "time_limit_seconds": 180,
        "locked": True,
        "required_previous_room": "room-3",
        "unlock_condition": {
            "type": "room_escaped",
            "room_id": "room-3",
            "description": "Escape room-3 (The Storage Archive) to unlock.",
        },
        "hints": [
            "Permissions are calculated in octal: read is 4, write is 2, execute is 1.",
            "Owner read-write is 6, group read is 4, others read is 4.",
        ],
        "escape_condition": {
            "puzzle_id": "4",
            "type": "puzzle_solved",
            "description": "Set proper rw-r--r-- permissions on the gate key.",
        },
        "objects": [
            {
                "id": "obj-security-console",
                "name": "Security Interlock Console",
                "description": "Displays posix file permission matrices and access bitmasks.",
                "is_pickupable": False,
                "interaction_hint": "Interact to inspect chmod mask expectations.",
                "triggers": [
                    {
                        "action": "examine",
                        "message": "Current Gate Requirement: POSIX chmod mode 644 (rw-r--r--).",
                        "state_effect": "mode_requirement_read",
                    }
                ],
            }
        ],
    },
    {
        "id": "room-5",
        "name": "The Central Core",
        "description": (
            "The heart of the facility. "
            "You need to provide the ultimate answer to escape to freedom."
        ),
        "difficulty": 4,
        "time_limit_seconds": 120,
        "locked": True,
        "required_previous_room": "room-4",
        "unlock_condition": {
            "type": "room_escaped",
            "room_id": "room-4",
            "description": "Escape room-4 (The Access Gate) to unlock.",
        },
        "hints": [
            "Write a C program that outputs the ultimate answer.",
            "Standard printf with number 42.",
        ],
        "escape_condition": {
            "puzzle_id": "5",
            "type": "puzzle_solved",
            "description": "Execute the 42 program in the sandbox to complete the escape.",
        },
        "objects": [
            {
                "id": "obj-core-reactor",
                "name": "Quantum AI Core Reactor",
                "description": "Pulsing reactor core waiting for numeric computation.",
                "is_pickupable": False,
                "interaction_hint": "Interact to awaken the core computation engine.",
                "triggers": [
                    {
                        "action": "examine",
                        "message": "Core: Awaiting calculation program. Expecting 42.",
                        "state_effect": "core_analyzed",
                    }
                ],
            }
        ],
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


def get_room_objects(room_id: str) -> Optional[List[Dict[str, Any]]]:
    """Return the list of interactive objects for a given room."""
    room = get_room(room_id)
    if not room:
        return None
    return copy.deepcopy(room.get("objects", []))


def get_room_object(room_id: str, object_id: str) -> Optional[Dict[str, Any]]:
    """Return a specific object from a room by object_id."""
    objects = get_room_objects(room_id)
    if objects is None:
        return None
    for obj in objects:
        if obj["id"] == str(object_id):
            return copy.deepcopy(obj)
    return None


def interact_with_object(
    room_id: str,
    object_id: str,
    action: str = "interact",
    state: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Perform an interaction on an object within a room."""
    obj = get_room_object(room_id, object_id)
    if not obj:
        return None

    action_clean = action.strip().lower() if action else "interact"
    triggers = obj.get("triggers", [])
    matched_trigger = None

    for t in triggers:
        if t.get("action", "").lower() == action_clean:
            matched_trigger = t
            break

    # If no exact trigger match, use the first trigger or a default fallback
    if not matched_trigger and triggers:
        matched_trigger = triggers[0]

    result: Dict[str, Any] = {
        "room_id": room_id,
        "object_id": object_id,
        "object_name": obj.get("name"),
        "action": action_clean,
        "success": True,
        "description": obj.get("description", ""),
        "is_pickupable": obj.get("is_pickupable", False),
        "message": (
            matched_trigger.get("message")
            if matched_trigger
            else f"You interacted with {obj.get('name')}."
        ),
        "state_effect": (
            matched_trigger.get("state_effect") if matched_trigger else None
        ),
    }

    return result


def check_unlock_condition(
    condition: Optional[Dict[str, Any]],
    escaped_rooms: set[str] | list[str],
    state: Optional[Dict[str, Any]] = None,
) -> bool:
    """Evaluate whether an unlock condition dictionary is satisfied."""
    if not condition:
        return True

    escaped_set = set(escaped_rooms)
    cond_type = condition.get("type")

    if cond_type == "starter":
        return True
    if cond_type == "room_escaped":
        req_room = condition.get("room_id")
        return bool(req_room and req_room in escaped_set)
    if cond_type == "min_escaped_count":
        min_count = int(condition.get("count", 0))
        return len(escaped_set) >= min_count
    if cond_type == "achievement" and state:
        ach_key = condition.get("achievement_id")
        return bool(ach_key and ach_key in state.get("achievements", {}))

    return True


def is_room_unlocked(
    room: Dict[str, Any],
    escaped_rooms: set[str] | list[str],
    state: Optional[Dict[str, Any]] = None,
) -> bool:
    """Determine whether a room is unlocked based on default locked status and unlock condition."""
    escaped_set = set(escaped_rooms)

    # Check if timer has expired on a timed room
    if state and room.get("time_limit_seconds") and room["id"] not in escaped_set:
        import storage

        timer = storage.get_room_timer(
            state, room["id"], default_limit=room.get("time_limit_seconds")
        )
        if timer and timer.get("is_expired"):
            return False

    if not room.get("locked", False):
        return True

    req = room.get("required_previous_room")
    if req and req not in escaped_set:
        return False

    cond = room.get("unlock_condition")
    return check_unlock_condition(cond, escaped_set, state)


def decorate_room(
    room: Dict[str, Any],
    escaped_rooms: set[str] | list[str],
    state: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Decorate a room dict with dynamic status, lock flags, objects, and unlock instructions."""
    escaped_set = set(escaped_rooms)
    r = copy.deepcopy(room)
    is_escaped = r["id"] in escaped_set
    unlocked = is_room_unlocked(r, escaped_set, state)

    # Inspect timer status
    timer_info = None
    if state and r.get("time_limit_seconds"):
        import storage

        timer_info = storage.get_room_timer(
            state, r["id"], default_limit=r.get("time_limit_seconds")
        )

    is_expired = bool(timer_info and timer_info.get("is_expired")) if not is_escaped else False

    if is_escaped:
        status = "escaped"
    elif is_expired:
        status = "expired"
    elif unlocked:
        status = "unlocked"
    else:
        status = "locked"

    unlock_info = r.get("unlock_condition") or {}
    unlock_desc = unlock_info.get("description")
    if is_expired:
        unlock_desc = f"Time limit expired ({r.get('time_limit_seconds')}s). Reset room to retry."
    elif not unlock_desc:
        req = r.get("required_previous_room")
        if req:
            unlock_desc = f"Complete and escape {req} to unlock."
        else:
            unlock_desc = "Available to explore."

    r["is_unlocked"] = unlocked
    r["is_escaped"] = is_escaped
    r["is_expired"] = is_expired
    r["status"] = status
    r["timer"] = timer_info
    r["unlock_instruction"] = unlock_desc
    return r


def get_rooms_summary(
    escaped_rooms: set[str] | list[str],
    state: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Return all rooms decorated with their current unlock/escape status."""
    return [decorate_room(room, escaped_rooms, state) for room in DEFAULT_ROOMS]
