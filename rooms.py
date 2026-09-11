from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional

# Default room catalog with interactive objects, triggers, hints, progression, atmosphere & themes
DEFAULT_ROOMS: List[Dict[str, Any]] = [
    {
        "id": "room-1",
        "name": "The Antechamber",
        "description": (
            "A dimly lit room with flickering monitors. "
            "The door is sealed by a basic terminal lock."
        ),
        "theme": "cyberpunk-terminal",
        "atmosphere": {
            "sights": (
                "Phosphor-green CRT glare reflecting against damp "
                "concrete and tangled ribbon cables."
            ),
            "sounds": (
                "A steady electrical hum punctuated by the intermittent click of cooling relays."
            ),
            "smells": "Faint ozone and warm silicon dust from decades of continuous uptime.",
            "ambient_text": (
                "You stand in the entrance vestibule. Phosphor-green light spills from a "
                "solitary CRT terminal across scuffed floor tiles. Cold air circulates from "
                "an overhead vent, and distant whisper of cooling fans echoes down the corridor."
            ),
            "ascii_art": (
                "+-----------------------------+\n"
                "| [CRT]       [FUSE]          |\n"
                "|  ||           ||            |\n"
                "|                             |\n"
                "| [KEYCARD]         [DOOR: #1]| \n"
                "+-----------------------------+"
            ),
        },
        "difficulty": 1,
        "time_limit_seconds": None,
        "position": {"x": 0, "y": 1},
        "connected_rooms": ["room-2"],
        "locked": False,
        "required_previous_room": None,
        "unlock_condition": {
            "type": "starter",
            "description": "Initial unlocked entry point to the facility.",
        },
        "hints": [
            {
                "level": 1,
                "text": "Inspect the filesystem carefully for hidden clues.",
                "unlock_condition": "Immediate access / baseline observation",
            },
            {
                "level": 2,
                "text": "Hidden files in Unix systems usually start with a leading dot ('.').",
                "unlock_condition": "after 1 failed attempt or 30 seconds",
            },
            {
                "level": 3,
                "text": (
                    "Run 'ls -a' or find hidden configuration "
                    "files to uncover the unlock parameter."
                ),
                "unlock_condition": "after 3 failed attempts or 2 minutes",
            },
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
                "usable_on": ["room-1", "room-2", "obj-security-console"],
                "use_effect": "Unlocks magnetic access panels across early facility chambers.",
                "interaction_hint": "Pick up the keycard for secure room access.",
                "triggers": [
                    {
                        "action": "pickup",
                        "message": "You picked up the Brass Keycard with intact magnetic stripe.",
                        "state_effect": "has_brass_keycard",
                    },
                    {
                        "action": "use",
                        "message": (
                            "You swipe the Brass Keycard. "
                            "The security circuit chimes affirmatively."
                        ),
                        "state_effect": "keycard_swiped",
                    },
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
        "theme": "abandoned-lab",
        "atmosphere": {
            "sights": (
                "Yellowed tractor-feed paper cascading from wire racks "
                "and blinking status LEDs on rackmount nodes."
            ),
            "sounds": (
                "Rhythmic clatter of punch card readers and the "
                "rapid whir of a cooling turbine spinning up."
            ),
            "smells": (
                "Aged paper, machine lubricant, and clean dry airflow "
                "from pressurized server racks."
            ),
            "ambient_text": (
                "You step into an industrial build lab. Workbenches overflow with disassembled "
                "tape drives and binder copies of ANSI C specifications. A compiler console "
                "waits in standby mode, ready to build source code into an executable door trigger."
            ),
            "ascii_art": (
                "+-----------------------------+\n"
                "| [WORKSTATION]   [PUNCHCARDS]|\n"
                "|      ||             ||      |\n"
                "|                             |\n"
                "| [K&R MANUAL]      [GATE: #2]|\n"
                "+-----------------------------+"
            ),
        },
        "difficulty": 2,
        "time_limit_seconds": 300,
        "position": {"x": 1, "y": 1},
        "connected_rooms": ["room-1", "room-3"],
        "locked": True,
        "required_previous_room": "room-1",
        "unlock_condition": {
            "type": "room_escaped",
            "room_id": "room-1",
            "description": "Escape room-1 (The Antechamber) to unlock.",
        },
        "hints": [
            {
                "level": 1,
                "text": "Use the standard GCC compiler syntax for C programs.",
                "unlock_condition": "Immediate access / baseline observation",
            },
            {
                "level": 2,
                "text": "Make sure to specify the output binary filename with the -o flag.",
                "unlock_condition": "after 1 failed attempt or 60 seconds",
            },
            {
                "level": 3,
                "text": "Compile the source directly using: gcc -o hello hello.c",
                "unlock_condition": "after 3 failed attempts or 3 minutes",
            },
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
                            "Toolchain status: gcc 13.2.0 ready. Target: hello.c -> hello binary."
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
                "usable_on": ["room-2", "obj-compiler-workbench"],
                "use_effect": "Provides exact compilation and syntax examples.",
                "interaction_hint": "Take the manual with you for syntax lookup.",
                "triggers": [
                    {
                        "action": "pickup",
                        "message": "Added K&R C Reference Guide to your knowledge tools.",
                        "state_effect": "has_c_manual",
                    },
                    {
                        "action": "use",
                        "message": (
                            "You consult the K&R Guide: 'gcc -o output source.c' is verified."
                        ),
                        "state_effect": "compiler_syntax_consulted",
                    },
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
        "theme": "ancient-tomb-vault",
        "atmosphere": {
            "sights": (
                "Monolithic drive cages stretching to high ceilings, their "
                "blue activity strobes flickering like torches."
            ),
            "sounds": (
                "Deep low-frequency reverberations from spinning magnetic "
                "platters and actuator heads seeking sectors."
            ),
            "smells": "Chilled air and anti-static floor coating with a touch of metal oxide.",
            "ambient_text": (
                "The archive vault opens into a subterranean chamber of towering drive "
                "enclosures. A maze of magnetic storage racks echoes with sector seek noise. "
                "Somewhere in the clutter of historical dumps, oversized data blocks are choking "
                "the passage forward."
            ),
            "ascii_art": (
                "+-----------------------------+\n"
                "| [TAPE RACKS]    [VENT SHAFT]|\n"
                "|     ||              ||      |\n"
                "|                             |\n"
                "| [BYTE SCANNER]    [GATE: #3]|\n"
                "+-----------------------------+"
            ),
        },
        "difficulty": 2,
        "time_limit_seconds": 240,
        "position": {"x": 2, "y": 1},
        "connected_rooms": ["room-2", "room-4"],
        "locked": True,
        "required_previous_room": "room-2",
        "unlock_condition": {
            "type": "room_escaped",
            "room_id": "room-2",
            "description": "Escape room-2 (The Compiler Laboratory) to unlock.",
        },
        "hints": [
            {
                "level": 1,
                "text": "The standard Unix find command can filter files by size thresholds.",
                "unlock_condition": "Immediate access / baseline observation",
            },
            {
                "level": 2,
                "text": "Look for files exceeding 1MB using the '+1M' or '+1024k' size flag.",
                "unlock_condition": "after 1 failed attempt or 60 seconds",
            },
            {
                "level": 3,
                "text": "Run 'find /archive -type f -size +1M' to locate blocking large files.",
                "unlock_condition": "after 3 failed attempts or 3 minutes",
            },
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
                            "Sector Index: Multiple large dumps found in /archive spanning >1MB."
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
                "usable_on": ["room-3", "obj-storage-rack"],
                "use_effect": "Calibrates sector scan thresholds to locate >1MB blocks.",
                "interaction_hint": "Pick up the byte scanner.",
                "triggers": [
                    {
                        "action": "pickup",
                        "message": "Acquired Handheld Byte Scanner.",
                        "state_effect": "has_byte_scanner",
                    },
                    {
                        "action": "use",
                        "message": (
                            "You activate the Handheld Byte Scanner. "
                            "High-density sectors pinpointed."
                        ),
                        "state_effect": "scanner_activated",
                    },
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
        "theme": "security-interlock",
        "atmosphere": {
            "sights": (
                "A reinforced titanium bulkhead with hydraulic pistons "
                "and illuminated chmod permission bit indicators."
            ),
            "sounds": (
                "Intermittent warning klaxons and the heavy clunk of pneumatic pressure seals."
            ),
            "smells": "Hydraulic fluid, scorched carbon contacts, and industrial rubber gaskets.",
            "ambient_text": (
                "A reinforced security airlock seals the corridor. Red emergency strips pulse "
                "across the bulkhead door. A permissions matrix terminal demands exact octal mode "
                "compliance before the hydraulic locking pins will disengage."
            ),
            "ascii_art": (
                "+-----------------------------+\n"
                "| [PERM MATRIX]  [HYDRAULICS] |\n"
                "|      ||             ||      |\n"
                "|                             |\n"
                "| [CONSOLE]       [BLAST DOOR]|\n"
                "+-----------------------------+"
            ),
        },
        "difficulty": 3,
        "time_limit_seconds": 180,
        "position": {"x": 3, "y": 1},
        "connected_rooms": ["room-3", "room-5"],
        "locked": True,
        "required_previous_room": "room-3",
        "unlock_condition": {
            "type": "room_escaped",
            "room_id": "room-3",
            "description": "Escape room-3 (The Storage Archive) to unlock.",
        },
        "hints": [
            {
                "level": 1,
                "text": "POSIX file permissions are in octal: read=4, write=2, execute=1.",
                "unlock_condition": "Immediate access / baseline observation",
            },
            {
                "level": 2,
                "text": "Owner read-write is 6 (4+2), group read is 4, others read is 4.",
                "unlock_condition": "after 1 failed attempt or 60 seconds",
            },
            {
                "level": 3,
                "text": (
                    "Execute 'chmod 644 <gate_key>' to grant owner read-write and others read-only."
                ),
                "unlock_condition": "after 3 failed attempts or 2 minutes",
            },
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
        "theme": "quantum-core",
        "atmosphere": {
            "sights": (
                "A glowing cylindrical magnetic containment column floating "
                "above an abyss of superconducting coils."
            ),
            "sounds": (
                "Harmonic resonant singing from the core containment field "
                "and high-pitched frequency oscillations."
            ),
            "smells": "Liquid helium vapor and ultra-pure ionized atmosphere.",
            "ambient_text": (
                "You have breached the facility's quantum core sanctuary. Superheated plasma "
                "spirals within a levitating torus. The central AI awaits the canonical "
                "computation code to finalize safe facility shutdown and grant absolute freedom."
            ),
            "ascii_art": (
                "+-----------------------------+\n"
                "|       ( ( ( CORE ) ) )      |\n"
                "|             / | \\           |\n"
                "|            /  |  \\          |\n"
                "| [TERMINAL]     [FINAL ESCAPE|\n"
                "+-----------------------------+"
            ),
        },
        "difficulty": 4,
        "time_limit_seconds": 120,
        "position": {"x": 4, "y": 1},
        "connected_rooms": ["room-4"],
        "locked": True,
        "required_previous_room": "room-4",
        "unlock_condition": {
            "type": "room_escaped",
            "room_id": "room-4",
            "description": "Escape room-4 (The Access Gate) to unlock.",
        },
        "hints": [
            {
                "level": 1,
                "text": "Write a C program that compiles and outputs the ultimate answer.",
                "unlock_condition": "Immediate access / baseline observation",
            },
            {
                "level": 2,
                "text": "Use standard printf() from <stdio.h> to print 42 with a newline.",
                "unlock_condition": "after 1 failed attempt or 30 seconds",
            },
            {
                "level": 3,
                "text": (
                    'The exact C code: #include <stdio.h>\\nint main(){printf("42\\\\n");return 0;}'
                ),
                "unlock_condition": "after 3 failed attempts or 1 minute",
            },
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
    {
        "id": "room-secret-1",
        "name": "The Hidden Glitch Sanctuary",
        "description": (
            "A concealed debug void accessed through a wall terminal glitch. "
            "Easter egg secrets and legacy test routines reside here."
        ),
        "theme": "debug-void",
        "is_secret": True,
        "discovery_condition": {
            "type": "terminal_glitch",
            "required_object": "obj-flickering-terminal",
            "action": "examine",
            "trigger_code": "glitch_void",
            "description": "Examine the flickering terminal in room-1 to reveal the hidden glitch frequency.",
        },
        "atmosphere": {
            "sights": "Inverted purple phosphor text floating in black space with scanline artifacts.",
            "sounds": "Lo-fi synth chords echoing across an endless virtual expanse.",
            "smells": "Virtual rain and ozone static.",
            "ambient_text": (
                "You stepped behind the render layer into a forgotten developer sanctuary. "
                "Unused assets and debug tools sit neatly categorized along glowing neon grids."
            ),
            "ascii_art": (
                "+-----------------------------+\n"
                "| [DEBUG CONSOLE]    [EASTER] |\n"
                "|       ||              ||    |\n"
                "|                             |\n"
                "| [SECRET DISK]    [VOID GATE]|\n"
                "+-----------------------------+"
            ),
        },
        "difficulty": 1,
        "time_limit_seconds": None,
        "position": {"x": 0, "y": 0},
        "connected_rooms": ["room-1"],
        "locked": False,
        "required_previous_room": None,
        "unlock_condition": {
            "type": "starter",
            "description": "Secret chamber revealed by discovery.",
        },
        "hints": [
            {
                "level": 1,
                "text": "The developer left an easter egg in the debug prompt.",
                "unlock_condition": "Immediate access / baseline observation",
            }
        ],
        "escape_condition": {
            "puzzle_id": "1",
            "type": "puzzle_solved",
            "description": "Claim the secret chamber easter egg.",
        },
        "objects": [
            {
                "id": "obj-debug-easter-egg",
                "name": "Developer Golden Floppy",
                "description": "A shiny golden 3.5-inch floppy disk labeled 'Lux v0.0.1 Easter Egg'.",
                "is_pickupable": True,
                "usable_on": ["room-secret-1", "room-1"],
                "use_effect": "Plays the classic retro victory chime.",
                "interaction_hint": "Collect the developer floppy disk.",
                "triggers": [
                    {
                        "action": "pickup",
                        "message": "You acquired the Golden Floppy Easter Egg! Tux and Pingu would be proud.",
                        "state_effect": "has_golden_floppy",
                    }
                ],
            }
        ],
    },
    {
        "id": "room-secret-2",
        "name": "The Cyber Crypt of Tux",
        "description": (
            "A retro Linux vault honoring Tux and Pingu with cryptic assembly riddles."
        ),
        "theme": "retro-monolith",
        "is_secret": True,
        "discovery_condition": {
            "type": "inventory_item_use",
            "required_item": "obj-brass-keycard",
            "target_room": "room-2",
            "description": "Use the Brass Keycard in room-2 on the mainframe workstation to unveil the Crypt.",
        },
        "atmosphere": {
            "sights": "A stone-and-silicon crypt lit by torches of blue LED fiber optics.",
            "sounds": "The faint noot-noot echo of mascot legends in the distance.",
            "smells": "Cedar wood mixed with cryogenic refrigeration chill.",
            "ambient_text": (
                "Monolithic stone tablets carved with hexadecimal opcodes rise from the floor. "
                "In the center rests the legendary monument to Lux the penguin mascot."
            ),
            "ascii_art": (
                "+-----------------------------+\n"
                "|       (o_  [LUX]  _o)       |\n"
                "|       //\\         /\\\\       |\n"
                "|       V_/_       _\\_V       |\n"
                "| [CRYPTO VAULT]  [TUX SHRINE]|\n"
                "+-----------------------------+"
            ),
        },
        "difficulty": 2,
        "time_limit_seconds": None,
        "position": {"x": 1, "y": 0},
        "connected_rooms": ["room-2"],
        "locked": False,
        "required_previous_room": None,
        "unlock_condition": {
            "type": "starter",
            "description": "Secret chamber unlocked upon discovery.",
        },
        "hints": [
            {
                "level": 1,
                "text": "Honor the penguin roots with Linux command knowledge.",
                "unlock_condition": "Immediate access / baseline observation",
            }
        ],
        "escape_condition": {
            "puzzle_id": "2",
            "type": "puzzle_solved",
            "description": "Solve the crypt riddle to escape.",
        },
        "objects": [
            {
                "id": "obj-tux-mascot-totem",
                "name": "Lux Penguin Totem",
                "description": "A handcrafted marble totem of Lux the penguin with sunglasses.",
                "is_pickupable": True,
                "usable_on": ["room-secret-2"],
                "use_effect": "Unlocks eternal penguin luck and blessing.",
                "interaction_hint": "Pick up the mascot totem.",
                "triggers": [
                    {
                        "action": "pickup",
                        "message": "You received the Lux Penguin Mascot Totem!",
                        "state_effect": "has_lux_totem",
                    }
                ],
            }
        ],
    },
]


def get_all_secret_room_ids() -> List[str]:
    """Return all secret room IDs in the catalog."""
    return [r["id"] for r in DEFAULT_ROOMS if r.get("is_secret", False)]


def get_all_rooms(include_secrets: bool = False, state: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Return a deep copy of configured rooms. Secret rooms are omitted unless discovered or requested."""
    import storage
    if include_secrets:
        return copy.deepcopy(DEFAULT_ROOMS)
    
    discovered_secrets = set(storage.get_discovered_secret_rooms(state)) if state else set()
    return [
        copy.deepcopy(r)
        for r in DEFAULT_ROOMS
        if not r.get("is_secret", False) or r["id"] in discovered_secrets
    ]



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


def find_object_across_rooms(object_id: str) -> Optional[Dict[str, Any]]:
    """Search all rooms for an object with the given ID."""
    oid = str(object_id).strip()
    for room in DEFAULT_ROOMS:
        for obj in room.get("objects", []):
            if obj["id"] == oid:
                return copy.deepcopy(obj)
    return None


def pickup_object(
    room_id: str,
    object_id: str,
    state: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Pick up a pickupable object in the given room and add to state inventory."""
    import storage

    obj = get_room_object(room_id, object_id)
    if not obj:
        return None

    if not obj.get("is_pickupable", False):
        return {
            "room_id": room_id,
            "object_id": object_id,
            "object_name": obj.get("name"),
            "success": False,
            "error": f"The object '{obj.get('name')}' is fixed in place and cannot be picked up.",
            "inventory": storage.get_inventory(state),
        }

    storage.add_inventory_item(state, object_id)
    triggers = obj.get("triggers", [])
    pickup_trigger = next((t for t in triggers if t.get("action") == "pickup"), None)
    msg = (
        pickup_trigger.get("message")
        if pickup_trigger
        else f"You collected {obj.get('name')} into your inventory."
    )
    effect = pickup_trigger.get("state_effect") if pickup_trigger else "item_collected"

    return {
        "room_id": room_id,
        "object_id": object_id,
        "object_name": obj.get("name"),
        "success": True,
        "message": msg,
        "state_effect": effect,
        "inventory": storage.get_inventory(state),
    }


def use_object(
    room_id: str,
    object_id: str,
    target_id: Optional[str] = None,
    state: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Use an inventory object in a room or against a specific target."""
    import storage

    if state is None:
        state = storage.load_state()

    obj = find_object_across_rooms(object_id)
    if not obj:
        return None

    inventory = storage.get_inventory(state)
    if object_id not in inventory:
        return {
            "room_id": room_id,
            "object_id": object_id,
            "object_name": obj.get("name"),
            "success": False,
            "error": f"You do not possess '{obj.get('name')}' in your inventory.",
            "inventory": inventory,
        }

    usable_on = obj.get("usable_on", [])
    target = target_id.strip() if target_id else room_id
    is_valid_target = True
    if usable_on:
        is_valid_target = (room_id in usable_on) or (target in usable_on)

    triggers = obj.get("triggers", [])
    use_trigger = next((t for t in triggers if t.get("action") == "use"), None)

    if not is_valid_target:
        return {
            "room_id": room_id,
            "object_id": object_id,
            "object_name": obj.get("name"),
            "target_id": target,
            "success": False,
            "error": f"Cannot use '{obj.get('name')}' here or on target '{target}'.",
            "inventory": inventory,
        }

    msg = use_trigger.get("message") if use_trigger else f"You used {obj.get('name')} successfully."
    effect = use_trigger.get("state_effect") if use_trigger else "item_used"

    return {
        "room_id": room_id,
        "object_id": object_id,
        "object_name": obj.get("name"),
        "target_id": target,
        "success": True,
        "message": msg,
        "state_effect": effect,
        "use_effect": obj.get("use_effect", ""),
        "inventory": inventory,
    }


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

    if action_clean == "pickup" and state is not None:
        return pickup_object(room_id, object_id, state)

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
        "state_effect": (matched_trigger.get("state_effect") if matched_trigger else None),
    }

    return result


def get_adaptive_room_hints(
    room_id: str,
    state: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Calculate and return unlocked adaptive hints for a room based on player attempts/progress."""
    import storage

    room = get_room(room_id)
    if not room:
        return None

    if state is None:
        state = storage.load_state()

    puzzle_id = room.get("escape_condition", {}).get("puzzle_id")
    failed_attempts = 0
    total_attempts = 0
    if puzzle_id:
        stats = storage.get_level_attempt_stats(state, puzzle_id)
        failed_attempts = int(stats.get("incorrect", 0) or 0)
        total_attempts = int(stats.get("attempts", 0) or 0)

    # Determine max unlocked level based on failed attempts
    # level 1: always available (0+ attempts)
    # level 2: unlocked after 1+ failed attempts or 2+ total attempts
    # level 3: unlocked after 3+ failed attempts or 4+ total attempts
    if failed_attempts >= 3 or total_attempts >= 4:
        max_unlocked_level = 3
    elif failed_attempts >= 1 or total_attempts >= 2:
        max_unlocked_level = 2
    else:
        max_unlocked_level = 1

    raw_hints = room.get("hints", [])
    hints_output = []
    unlocked_count = 0

    for h in raw_hints:
        if isinstance(h, dict):
            lvl = int(h.get("level", 1))
            is_unlocked = lvl <= max_unlocked_level
            locked_placeholder = "Locked. Make more attempts or spend time exploring to reveal."
            hint_entry = {
                "level": lvl,
                "text": h.get("text", "") if is_unlocked else locked_placeholder,
                "unlock_condition": h.get("unlock_condition", ""),
                "is_unlocked": is_unlocked,
            }
        else:
            # Fallback for simple string hint
            lvl = 1
            is_unlocked = True
            hint_entry = {
                "level": lvl,
                "text": str(h),
                "unlock_condition": "Available",
                "is_unlocked": True,
            }
        if is_unlocked:
            unlocked_count += 1
        hints_output.append(hint_entry)

    # Filter available text list for straightforward display
    available_hint_texts = [h["text"] for h in hints_output if h["is_unlocked"]]

    return {
        "room_id": room_id,
        "room_name": room.get("name"),
        "difficulty": room.get("difficulty"),
        "puzzle_id": puzzle_id,
        "failed_attempts": failed_attempts,
        "total_attempts": total_attempts,
        "max_unlocked_level": max_unlocked_level,
        "unlocked_hints_count": unlocked_count,
        "total_hints_count": len(hints_output),
        "hints": hints_output,
        "available_hints": available_hint_texts,
    }


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

    # Compute adaptive hints
    adaptive_hint_info = get_adaptive_room_hints(r["id"], state=state)
    if adaptive_hint_info:
        r["hints_data"] = adaptive_hint_info
        r["hints"] = adaptive_hint_info.get("hints", [])

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
    include_secrets: bool = False,
) -> List[Dict[str, Any]]:
    """Return all accessible rooms decorated with their current unlock/escape status."""
    rooms_list = get_all_rooms(include_secrets=include_secrets, state=state)
    return [decorate_room(room, escaped_rooms, state) for room in rooms_list]


def get_rooms_map(
    state: Optional[Dict[str, Any]] = None,
    current_room_id: Optional[str] = None,
    include_secrets: bool = False,
) -> Dict[str, Any]:
    """Return room map structure with positions, connections, and unlock/escape statuses."""
    import storage

    if state is None:
        state = storage.load_state()

    escaped_rooms = storage.get_escaped_rooms(state)
    decorated = get_rooms_summary(escaped_rooms, state=state, include_secrets=include_secrets)

    # Determine default current room if not explicitly provided
    # If not provided, find the first unlocked but unescaped room, or the last escaped room
    if not current_room_id:
        active_room = next(
            (r["id"] for r in decorated if r.get("is_unlocked") and not r.get("is_escaped")),
            None,
        )
        if not active_room and decorated:
            active_room = decorated[-1]["id"]
        current_room_id = active_room or "room-1"

    connections = []
    seen_edges = set()
    for r in decorated:
        for target in r.get("connected_rooms", []):
            edge = tuple(sorted([r["id"], target]))
            if edge not in seen_edges:
                seen_edges.add(edge)
                connections.append({"from": r["id"], "to": target})

    xs = [r.get("position", {}).get("x", 0) for r in decorated if r.get("position")]
    ys = [r.get("position", {}).get("y", 0) for r in decorated if r.get("position")]

    grid = {
        "min_x": min(xs) if xs else 0,
        "max_x": max(xs) if xs else 0,
        "min_y": min(ys) if ys else 0,
        "max_y": max(ys) if ys else 0,
        "total_rooms": len(decorated),
        "escaped_count": len(escaped_rooms),
    }

    return {
        "rooms": decorated,
        "connections": connections,
        "current_room_id": current_room_id,
        "escaped_rooms": escaped_rooms,
        "grid": grid,
    }

