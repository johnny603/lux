import os
from datetime import datetime

from flask import Flask, jsonify, render_template, request
from flask_wtf import CSRFProtect

import contributors
import game_systems
import leaderboard
import learning_paths
import puzzle_generator
import storage
from sandbox import DockerSandbox, get_runtime

app = Flask(__name__)
app.secret_key = os.getenv("LUX_SECRET_KEY") or os.urandom(32).hex()
app.config["WTF_CSRF_SECRET_KEY"] = os.getenv("LUX_CSRF_SECRET_KEY") or os.urandom(32).hex()
ERROR_NOT_FOUND = "not found"
csrf = CSRFProtect(app)

PUZZLES = [
    {
        "id": "1",
        "title": "Linux: List hidden files",
        "description": "What ls flag shows hidden files?",
        "hint": "Think dotfiles",
        "validator": "equals",
        "flag": "-a",
    },
    {
        "id": "2",
        "title": "C: Compilation",
        "description": "Compile hello.c into hello using gcc",
        "hint": "gcc input output",
        "validator": "equals",
        "flag": "gcc hello.c -o hello",
    },
    {
        "id": "3",
        "title": "Linux: Find large files",
        "description": "Find files larger than 1MB",
        "hint": "use find -size",
        "validator": "contains",
        "flag": "-size +1M",
    },
    {
        "id": "4",
        "title": "Permissions",
        "description": "Set rw-r--r-- permissions",
        "hint": "644 is octal",
        "validator": "equals",
        "flag": "chmod 644 <file>",
    },
    {
        "id": "5",
        "title": "Print 42",
        "description": "Write C program printing 42",
        "hint": "printf",
        "validator": "script",
        "test_script": "gcc answer.c -o answer && ./answer | grep -xq '42'",
    },
    {
        "id": "6",
        "title": "Linux: Parent directory",
        "description": "What command moves you up one directory?",
        "hint": "Think directory traversal",
        "validator": "equals",
        "flag": "cd ..",
    },
    {
        "id": "7",
        "title": "Linux: Process list",
        "description": "What command shows the running processes for the current terminal?",
        "hint": "Use ps with a broad view",
        "validator": "equals",
        "flag": "ps aux",
    },
    {
        "id": "8",
        "title": "Linux: Listening ports",
        "description": "What command shows listening TCP ports?",
        "hint": "ss can inspect sockets",
        "validator": "equals",
        "flag": "ss -tln",
    },
    {
        "id": "9",
        "title": "Linux: Refresh packages",
        "description": "What command refreshes package lists on Debian or Ubuntu?",
        "hint": "apt has an update subcommand",
        "validator": "equals",
        "flag": "apt update",
    },
    {
        "id": "10",
        "title": "Linux: Shell loop",
        "description": "What one-liner prints each .txt file in the current directory?",
        "hint": "Use a for loop and echo",
        "validator": "contains",
        "flag": 'for f in *.txt; do echo "$f"; done',
    },
    {
        "id": "11",
        "title": "Linux: Permissions and ownership",
        "description": (
            "What commands set report.txt to rw-r----- and change its owner to alice:staff?"
        ),
        "hint": "Use chmod and chown together",
        "validator": "contains",
        "flag": "chmod 640 report.txt && chown alice:staff report.txt",
    },
    {
        "id": "12",
        "title": "Linux: Log inspection",
        "description": "What command shows the most recent 20 systemd journal entries?",
        "hint": "journalctl has a count option",
        "validator": "equals",
        "flag": "journalctl -n 20",
    },
    {
        "id": "13",
        "title": "Linux: Disk usage",
        "description": "What command shows human-readable disk usage for mounted filesystems?",
        "hint": "Use df with a human-readable flag",
        "validator": "equals",
        "flag": "df -h",
    },
    {
        "id": "14",
        "title": "Bash challenge: Count lines",
        "description": (
            "Write answer.sh so that sh answer.sh input.txt prints the number of lines in the file."
        ),
        "hint": "wc -l can help",
        "validator": "script",
        "test_script": (
            "printf 'alpha\nbeta\ngamma\n' > input.txt && sh answer.sh input.txt | grep -xq '3'"
        ),
    },
    {
        "id": "15",
        "title": "Bash challenge: Filter TODOs",
        "description": (
            "Write answer.sh so that sh answer.sh notes.txt prints only lines that start with TODO."
        ),
        "hint": "grep with a start-of-line anchor is enough",
        "validator": "script",
        "test_script": (
            "printf 'TODO first\nskip\nTODO second\n' > notes.txt "
            "&& sh answer.sh notes.txt | grep -xq 'TODO first' "
            "&& sh answer.sh notes.txt | grep -xq 'TODO second'"
        ),
    },
    {
        "id": "16",
        "title": "C: Intermediate pointers",
        "description": (
            "Write answer.c so it prints the second value from the array {10, 20, 30} "
            "by dereferencing a pointer."
        ),
        "hint": "Use pointer arithmetic or array indexing.",
        "validator": "script",
        "test_script": "gcc answer.c -o answer && ./answer | grep -xq '20'",
    },
    {
        "id": "17",
        "title": "C: Memory management",
        "description": (
            "Write answer.c so it allocates space for two integers, stores 40 and 2, "
            "frees the memory, and prints their sum."
        ),
        "hint": "malloc and free both matter here.",
        "validator": "script",
        "test_script": "gcc answer.c -o answer && ./answer | grep -xq '42'",
    },
    {
        "id": "18",
        "title": "C: Data structures",
        "description": (
            "Write answer.c so it builds a three-node linked list with values 1, 2, and 3, "
            "then prints the node count."
        ),
        "hint": "A struct with a next pointer is enough.",
        "validator": "script",
        "test_script": "gcc answer.c -o answer && ./answer | grep -xq '3'",
    },
    {
        "id": "19",
        "title": "C: Algorithms",
        "description": (
            "Write answer.c so it binary-searches the sorted array {5, 10, 15, 20, 25, 30, 35} "
            "for 25 and prints its index."
        ),
        "hint": "Divide the search space.",
        "validator": "script",
        "test_script": "gcc answer.c -o answer && ./answer | grep -xq '4'",
    },
    {
        "id": "20",
        "title": "Python: List comprehension",
        "description": (
            "Write answer.py so it defines nums = [1, 2, 3] and uses a list comprehension "
            "to print [1, 4, 9]."
        ),
        "hint": "Square each x inside a comprehension.",
        "validator": "script",
        "test_script": (
            "grep -Eq "
            "'squares[[:space:]]*=[[:space:]]*\\[x\\*x[[:space:]]+for[[:space:]]+"
            "x[[:space:]]+in[[:space:]]+nums\\]' answer.py "
            "&& grep -Eq 'print\\(squares\\)' answer.py"
        ),
    },
    {
        "id": "21",
        "title": "Java: Entry point",
        "description": (
            "Write Main.java so it contains a standard public static void main(String[] args) "
            "and prints ready."
        ),
        "hint": "main is the entry point.",
        "validator": "script",
        "test_script": (
            "grep -Eq "
            "'public[[:space:]]+static[[:space:]]+void[[:space:]]+main\\(String\\[\\]"
            "[[:space:]]+args\\)' Main.java "
            "&& grep -Eq 'System\\.out\\.println\\(\\\"ready\\\"\\);' Main.java"
        ),
    },
    {
        "id": "22",
        "title": "JavaScript: Strict equality",
        "description": (
            "Write answer.js so it compares left and right with strict equality "
            "and prints true when they match."
        ),
        "hint": "Use three equals signs.",
        "validator": "script",
        "test_script": "grep -Eq '===' answer.js && grep -Eq 'console\\.log\\(true\\)' answer.js",
    },
    {
        "id": "23",
        "title": "Web security: SQL injection",
        "description": (
            "Write answer.sh so it accepts only usernames from the allowlist "
            "alice, bob, or carol and prints ACCEPT when matched."
        ),
        "hint": "Known-good inputs only.",
        "validator": "script",
        "test_script": (
            "printf 'alice\n' | sh answer.sh | grep -xq 'ACCEPT' "
            "&& printf 'mallory\n' | sh answer.sh | grep -xq 'REJECT'"
        ),
    },
    {
        "id": "24",
        "title": "Reverse engineering: Strings",
        "description": (
            "Write answer.sh so it uses strings on the input binary "
            "and prints any line containing FLAG."
        ),
        "hint": "Extract printable text first.",
        "validator": "script",
        "test_script": (
            "printf 'abc\0FLAG{reverse_me}\0xyz' > sample.bin "
            "&& sh answer.sh sample.bin | grep -xq 'FLAG{reverse_me}'"
        ),
    },
    {
        "id": "25",
        "title": "Digital forensics: Hashing",
        "description": "Write answer.sh so it prints the SHA-256 checksum of evidence.bin.",
        "hint": "Use a checksum command from coreutils.",
        "validator": "script",
        "test_script": (
            "printf 'forensic data\n' > evidence.bin "
            "&& expected=$(sha256sum evidence.bin | awk '{print $1}') "
            '&& sh answer.sh evidence.bin | grep -xq "$expected"'
        ),
    },
    {
        "id": "26",
        "title": "Cryptography: Encoding",
        "description": "Write answer.sh so it base64-decodes encoded.txt and prints the plaintext.",
        "hint": "The encoding is reversible.",
        "validator": "script",
        "test_script": (
            "printf 'SGVsbG8=\n' > encoded.txt && sh answer.sh encoded.txt | grep -xq 'Hello'"
        ),
    },
    {
        "id": "27",
        "title": "Secure coding: Input validation",
        "description": (
            "Write answer.sh so it only accepts usernames matching ^[a-z][a-z0-9_]*$ "
            "and rejects anything else."
        ),
        "hint": "Validate input before using it.",
        "validator": "script",
        "test_script": (
            "printf 'alice1\n' | sh answer.sh | grep -xq 'VALID' "
            "&& printf 'Bad-Name\n' | sh answer.sh | grep -xq 'INVALID'"
        ),
    },
    {
        "id": "28",
        "title": "CTF beginner: File signature",
        "description": (
            "Write answer.sh so it reports the file type of the input using the file command."
        ),
        "hint": "Magic bytes reveal the type.",
        "validator": "script",
        "test_script": (
            "printf 'hello world\n' > note.txt && sh answer.sh note.txt | grep -qi 'text'"
        ),
    },
    {
        "id": "29",
        "title": "Docker: Run container",
        "description": (
            "Write answer.sh so it prints the exact command to run an interactive "
            "Ubuntu container and remove it on exit."
        ),
        "hint": "Combine --rm and -it.",
        "validator": "script",
        "test_script": "sh answer.sh | grep -xq 'docker run --rm -it ubuntu'",
    },
    {
        "id": "30",
        "title": "Git: Branch creation",
        "description": (
            "Write answer.sh so it initializes a repo and creates a new branch named feature/auth."
        ),
        "hint": "Use git checkout -b.",
        "validator": "script",
        "test_script": (
            "git init -q && sh answer.sh && git branch --show-current | grep -xq 'feature/auth'"
        ),
    },
    {
        "id": "31",
        "title": "CI/CD: GitHub Actions trigger",
        "description": "Write .github/workflows/ci.yml so the workflow triggers on push.",
        "hint": "The trigger key is short.",
        "validator": "script",
        "test_script": (
            "mkdir -p .github/workflows "
            "&& grep -Eq '^on:' .github/workflows/ci.yml "
            "&& grep -Eq 'push' .github/workflows/ci.yml"
        ),
    },
    {
        "id": "32",
        "title": "Cloud fundamentals: Shared model",
        "description": (
            "Write answer.sh so it prints IaaS when the prompt describes "
            "provider-managed hardware and customer-managed VMs."
        ),
        "hint": "The answer is an acronym.",
        "validator": "script",
        "test_script": (
            "printf 'provider hardware and virtual machines\n' | sh answer.sh | grep -xq 'IaaS'"
        ),
    },
]

PUZZLE_METADATA = {
    "1": {"category": "Linux", "difficulty": "easy", "tags": ["linux", "filesystem", "cli"]},
    "2": {"category": "Programming", "difficulty": "easy", "tags": ["c", "build", "gcc"]},
    "3": {"category": "Linux", "difficulty": "easy", "tags": ["linux", "find", "filesystem"]},
    "4": {
        "category": "Linux",
        "difficulty": "easy",
        "tags": ["linux", "permissions", "filesystem"],
    },
    "5": {"category": "Programming", "difficulty": "easy", "tags": ["c", "stdio", "compile"]},
    "6": {"category": "Linux", "difficulty": "easy", "tags": ["linux", "navigation", "shell"]},
    "7": {"category": "Linux", "difficulty": "easy", "tags": ["linux", "process", "ps"]},
    "8": {"category": "Linux", "difficulty": "easy", "tags": ["linux", "networking", "sockets"]},
    "9": {"category": "Linux", "difficulty": "easy", "tags": ["linux", "packages", "apt"]},
    "10": {"category": "Linux", "difficulty": "easy", "tags": ["linux", "bash", "loops"]},
    "11": {
        "category": "Linux",
        "difficulty": "medium",
        "tags": ["linux", "permissions", "ownership"],
    },
    "12": {"category": "Linux", "difficulty": "easy", "tags": ["linux", "logs", "systemd"]},
    "13": {"category": "Linux", "difficulty": "easy", "tags": ["linux", "disk", "df"]},
    "14": {"category": "Linux", "difficulty": "medium", "tags": ["bash", "scripting", "files"]},
    "15": {"category": "Linux", "difficulty": "medium", "tags": ["bash", "filtering", "grep"]},
    "16": {"category": "Programming", "difficulty": "medium", "tags": ["c", "pointers", "memory"]},
    "17": {"category": "Programming", "difficulty": "medium", "tags": ["c", "malloc", "free"]},
    "18": {
        "category": "Programming",
        "difficulty": "medium",
        "tags": ["c", "structs", "linked-lists"],
    },
    "19": {
        "category": "Programming",
        "difficulty": "medium",
        "tags": ["c", "algorithms", "binary-search"],
    },
    "20": {
        "category": "Programming",
        "difficulty": "medium",
        "tags": ["python", "comprehensions", "lists"],
    },
    "21": {
        "category": "Programming",
        "difficulty": "easy",
        "tags": ["java", "entry-point", "syntax"],
    },
    "22": {
        "category": "Programming",
        "difficulty": "easy",
        "tags": ["javascript", "operators", "equality"],
    },
    "23": {
        "category": "Cybersecurity",
        "difficulty": "medium",
        "tags": ["web-security", "allowlist", "input-validation"],
    },
    "24": {
        "category": "Cybersecurity",
        "difficulty": "medium",
        "tags": ["reverse-engineering", "strings", "binary"],
    },
    "25": {
        "category": "Cybersecurity",
        "difficulty": "easy",
        "tags": ["forensics", "hashing", "sha256"],
    },
    "26": {
        "category": "Cybersecurity",
        "difficulty": "easy",
        "tags": ["cryptography", "base64", "encoding"],
    },
    "27": {
        "category": "Cybersecurity",
        "difficulty": "medium",
        "tags": ["secure-coding", "validation", "regex"],
    },
    "28": {
        "category": "Cybersecurity",
        "difficulty": "easy",
        "tags": ["ctf", "file-signatures", "file"],
    },
    "29": {"category": "DevOps", "difficulty": "easy", "tags": ["docker", "containers", "cli"]},
    "30": {"category": "DevOps", "difficulty": "easy", "tags": ["git", "branches", "workflow"]},
    "31": {"category": "DevOps", "difficulty": "easy", "tags": ["ci-cd", "github-actions", "yaml"]},
    "32": {"category": "DevOps", "difficulty": "easy", "tags": ["cloud", "iaas", "fundamentals"]},
}

for puzzle in PUZZLES:
    puzzle.update(PUZZLE_METADATA.get(puzzle["id"], {}))


def get_puzzle(pid):
    return next((p for p in PUZZLES if p["id"] == pid), None)


def catalog_levels():
    return [
        {
            "id": p["id"],
            "title": p["title"],
            "description": p["description"],
            "hint": p["hint"],
            "validator": p.get("validator", "equals"),
            "category": p["category"],
            "difficulty": p["difficulty"],
            "tags": p["tags"],
        }
        for p in PUZZLES
    ]


def puzzle_summary(puzzle):
    return {
        "id": puzzle["id"],
        "title": puzzle["title"],
        "description": puzzle["description"],
        "hint": puzzle["hint"],
        "validator": puzzle.get("validator", "equals"),
        "category": puzzle["category"],
        "difficulty": puzzle["difficulty"],
        "tags": puzzle["tags"],
    }


def _submission_response(puzzle, attempt, files):
    result = validate(puzzle, attempt, files)
    if isinstance(result, tuple):
        payload = result[0].get_json()
        status = result[1]
    else:
        payload = result.get_json()
        status = result.status_code
    return payload, status


def response(ok=True, **kwargs):
    return jsonify({"ok": ok, **kwargs})


@app.route("/", methods=["GET"])
def index():
    return response(service="puzzle-server", time=datetime.now().isoformat())


@app.route("/health", methods=["GET"])
def health():
    return response(service="ok")


@app.route("/ready", methods=["GET"])
def ready():
    return response(service="ready")


@app.route("/levels", methods=["GET"])
def levels():
    return jsonify(
        [
            {
                "id": p["id"],
                "title": p["title"],
                "category": p["category"],
                "difficulty": p["difficulty"],
                "tags": p["tags"],
            }
            for p in PUZZLES
        ]
    )


@app.route("/level/<pid>", methods=["GET"])
def level(pid):
    p = get_puzzle(pid)
    if not p:
        return response(False, error=ERROR_NOT_FOUND), 404

    return jsonify(puzzle_summary(p))


@app.route("/submit", methods=["POST"])
@app.route("/api/v1/submit", methods=["POST"])
@csrf.exempt
def submit():
    data = request.json or {}

    pid = str(data.get("level_id", ""))
    attempt = (data.get("attempt") or "").strip()
    files = data.get("files") or {}

    if not pid:
        return response(False, error="missing level_id"), 400

    puzzle = get_puzzle(pid)
    if not puzzle:
        return response(False, error="invalid level"), 404

    return validate(puzzle, attempt, files)


@app.route("/api/v1/profile", methods=["GET", "PUT"])
def api_profile():
    state = storage.load_state()
    if request.method == "GET":
        return jsonify(storage.get_profile(state))
    data = request.json or {}
    profile = storage.update_profile(
        state,
        display_name=data.get("display_name"),
        preferences=data.get("preferences"),
    )
    storage.save_state(state)
    return jsonify(profile)


@app.route("/api/v1/leaderboard", methods=["GET"])
def api_leaderboard():
    state = storage.load_state()
    metric = (request.args.get("metric") or "solved_count").strip()
    return jsonify(leaderboard.get_leaderboard(state, catalog_levels(), metric=metric))


@app.route("/api/v1/learning-path", methods=["GET"])
def api_learning_path():
    state = storage.load_state()
    limit = int(request.args.get("limit", 5))
    return jsonify(learning_paths.build_learning_path(state, catalog_levels(), limit=limit))


@app.route("/api/v1/game/adventure", methods=["GET"])
def api_adventure():
    state = storage.load_state()
    return jsonify(game_systems.adventure_status(state, catalog_levels()))


@app.route("/api/v1/game/daily", methods=["GET"])
def api_daily():
    state = storage.load_state()
    return jsonify(game_systems.daily_challenge_status(state, catalog_levels()))


@app.route("/api/v1/puzzles/generate", methods=["POST"])
@csrf.exempt
def api_generate_puzzle():
    data = request.json or {}
    category = (data.get("category") or "Programming").strip()
    difficulty = (data.get("difficulty") or "easy").strip().lower()
    topic = (data.get("topic") or "practice").strip()
    existing_ids = {puzzle["id"] for puzzle in PUZZLES}
    next_id = str(max(int(p["id"]) for p in PUZZLES) + 1)
    try:
        generated = puzzle_generator.generate_puzzle_with_ai(
            category=category,
            difficulty=difficulty,
            topic=topic,
            existing_ids=existing_ids,
            next_id=next_id,
        )
    except Exception as exc:
        return response(False, error=str(exc)), 400
    return jsonify({"ok": True, "puzzle": generated})


@app.route("/profile", methods=["GET", "POST"])
def web_profile():
    state = storage.load_state()
    message = None
    if request.method == "POST":
        preferences = {
            "difficulty_preference": (request.form.get("difficulty_preference") or "any").strip(),
            "hint_style": (request.form.get("hint_style") or "concise").strip(),
            "show_solved_first": request.form.get("show_solved_first") == "on",
            "favorite_categories": [
                item.strip()
                for item in (request.form.get("favorite_categories") or "").split(",")
                if item.strip()
            ],
        }
        storage.update_profile(
            state,
            display_name=request.form.get("display_name"),
            preferences=preferences,
        )
        storage.save_state(state)
        leaderboard.upsert_local_entry(state, catalog_levels())
        message = "Profile saved."
    profile = storage.get_profile(state)
    return render_template(
        "profile.html",
        profile=profile,
        categories=sorted({lvl["category"] for lvl in catalog_levels()}),
        message=message,
    )


@app.route("/leaderboard", methods=["GET"])
def web_leaderboard():
    state = storage.load_state()
    metric = (request.args.get("metric") or "solved_count").strip()
    board = leaderboard.get_leaderboard(state, catalog_levels(), metric=metric)
    return render_template("leaderboard.html", board=board, metric=metric)


@app.route("/api/v1/levels", methods=["GET"])
def api_levels():
    return jsonify(catalog_levels())


@app.route("/api/v1/level/<pid>", methods=["GET"])
def api_level(pid):
    return level(pid)


@app.route("/api/v1/progress", methods=["GET"])
def api_progress():
    state = storage.load_state()
    return jsonify(
        {
            "progress": storage.get_progress_summary(state, catalog_levels()),
            "solved": list(storage.get_solved_levels(state)),
            "achievements": state.get("achievements", {}),
            "profile": state.get("profile", {"display_name": "Learner", "preferences": {}}),
        }
    )


@app.route("/api/v1/achievements", methods=["GET"])
def api_achievements():
    state = storage.load_state()
    return jsonify(state.get("achievements", {}))


@app.route("/api/v1/contributors", methods=["GET"])
def api_contributors():
    return jsonify({"contributors": contributors.load_contributors()})


@app.route("/contributors", methods=["GET"])
def web_contributors():
    return render_template("contributors.html", contributors=contributors.load_contributors())


@app.route("/web", methods=["GET"])
@app.route("/puzzles", methods=["GET"])
def web_puzzles():
    levels = catalog_levels()
    query = (request.args.get("q") or "").strip().lower()
    category = (request.args.get("category") or "").strip().lower()
    difficulty = (request.args.get("difficulty") or "").strip().lower()
    state = storage.load_state()
    solved = storage.get_solved_levels(state)

    if query:
        levels = [
            lvl
            for lvl in levels
            if query
            in " ".join(
                str(lvl.get(k, ""))
                for k in ("id", "title", "description", "category", "difficulty")
            ).lower()
        ]
    if category:
        levels = [lvl for lvl in levels if lvl.get("category", "").lower() == category]
    if difficulty:
        levels = [lvl for lvl in levels if lvl.get("difficulty", "").lower() == difficulty]

    return render_template(
        "index.html",
        levels=levels,
        solved=solved,
        progress=storage.get_progress_summary(state, catalog_levels()),
        categories=sorted({lvl["category"] for lvl in catalog_levels()}),
        selected_category=category,
        selected_difficulty=difficulty,
        search_query=request.args.get("q", ""),
        profile=state.get("profile", {"display_name": "Learner", "preferences": {}}),
    )


@app.route("/dashboard", methods=["GET"])
def dashboard():
    state = storage.load_state()
    levels = catalog_levels()
    summary = storage.get_progress_summary(state, levels)
    solved = storage.get_solved_levels(state)
    recent_levels = [
        get_puzzle(level_id)
        for level_id in state.get("meta", {}).get("recent_solved", [])
        if get_puzzle(level_id)
    ]
    return render_template(
        "dashboard.html",
        progress=summary,
        solved=solved,
        achievements=state.get("achievements", {}),
        profile=state.get("profile", {"display_name": "Learner", "preferences": {}}),
        recent_levels=recent_levels,
        total_levels=len(levels),
    )


@app.route("/puzzles/<pid>", methods=["GET"])
def web_puzzle_detail(pid):
    puzzle = get_puzzle(pid)
    if not puzzle:
        return response(False, error=ERROR_NOT_FOUND), 404
    state = storage.load_state()
    stats = storage.get_level_attempt_stats(state, pid)
    return render_template(
        "puzzle_detail.html",
        puzzle=puzzle_summary(puzzle),
        solved=pid in storage.get_solved_levels(state),
        stats=stats,
        progress=storage.get_progress_summary(state, catalog_levels()),
    )


@app.route("/puzzles/<pid>/submit", methods=["POST"])
def web_submit(pid):
    puzzle = get_puzzle(pid)
    if not puzzle:
        return response(False, error=ERROR_NOT_FOUND), 404

    attempt = (request.form.get("answer") or "").strip()
    files = {}
    for upload in request.files.getlist("files"):
        if upload and upload.filename:
            files[upload.filename] = upload.read().decode(errors="ignore")
    if puzzle.get("validator") == "script" and not files:
        return render_template(
            "result.html",
            puzzle=puzzle_summary(puzzle),
            result={"ok": False, "error": "upload at least one source file"},
            status=400,
        )

    payload, status = _submission_response(puzzle, attempt, files)
    return render_template(
        "result.html", puzzle=puzzle_summary(puzzle), result=payload, status=status
    )


def build_docker_command(source_dir):
    return DockerSandbox().build_command(source_dir)


def run_docker(files, script):
    return get_runtime().run(files, script)


def validate(puzzle, attempt, files):
    v = puzzle.get("validator", "equals")

    if v == "equals":
        correct = attempt == puzzle["flag"]
        return response(True, correct=correct, expected=None if correct else puzzle["flag"])

    if v == "contains":
        correct = puzzle["flag"] in attempt
        return response(True, correct=correct, expected=None if correct else puzzle["flag"])

    if v == "script":
        try:
            result = run_docker(files, puzzle["test_script"])
            return response(True, correct=result["passed"], output=result)
        except Exception as e:
            return response(False, error=str(e)), 500

    return response(False, error="unsupported validator"), 400


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
