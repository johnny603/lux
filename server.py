from flask import Flask, jsonify, request
from datetime import datetime
import subprocess
import tempfile
import os
import shutil

app = Flask(__name__)

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
        "flag": "for f in *.txt; do echo \"$f\"; done",
    },
    {
        "id": "11",
        "title": "Linux: Permissions and ownership",
        "description": "What commands set report.txt to rw-r----- and change its owner to alice:staff?",
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
        "description": "Write answer.sh so that sh answer.sh input.txt prints the number of lines in the file.",
        "hint": "wc -l can help",
        "validator": "script",
        "test_script": "printf 'alpha\nbeta\ngamma\n' > input.txt && sh answer.sh input.txt | grep -xq '3'",
    },
    {
        "id": "15",
        "title": "Bash challenge: Filter TODOs",
        "description": "Write answer.sh so that sh answer.sh notes.txt prints only lines that start with TODO.",
        "hint": "grep with a start-of-line anchor is enough",
        "validator": "script",
        "test_script": "printf 'TODO first\nskip\nTODO second\n' > notes.txt && sh answer.sh notes.txt | grep -xq 'TODO first' && sh answer.sh notes.txt | grep -xq 'TODO second'",
    },
    {
        "id": "16",
        "title": "C: Intermediate pointers",
        "description": "Write answer.c so it prints the second value from the array {10, 20, 30} by dereferencing a pointer.",
        "hint": "Use pointer arithmetic or array indexing.",
        "validator": "script",
        "test_script": "gcc answer.c -o answer && ./answer | grep -xq '20'",
    },
    {
        "id": "17",
        "title": "C: Memory management",
        "description": "Write answer.c so it allocates space for two integers, stores 40 and 2, frees the memory, and prints their sum.",
        "hint": "malloc and free both matter here.",
        "validator": "script",
        "test_script": "gcc answer.c -o answer && ./answer | grep -xq '42'",
    },
    {
        "id": "18",
        "title": "C: Data structures",
        "description": "Write answer.c so it builds a three-node linked list with values 1, 2, and 3, then prints the node count.",
        "hint": "A struct with a next pointer is enough.",
        "validator": "script",
        "test_script": "gcc answer.c -o answer && ./answer | grep -xq '3'",
    },
    {
        "id": "19",
        "title": "C: Algorithms",
        "description": "Write answer.c so it binary-searches the sorted array {5, 10, 15, 20, 25, 30, 35} for 25 and prints its index.",
        "hint": "Divide the search space.",
        "validator": "script",
        "test_script": "gcc answer.c -o answer && ./answer | grep -xq '4'",
    },
    {
        "id": "20",
        "title": "Python: List comprehension",
        "description": "Write answer.py so it defines nums = [1, 2, 3] and uses a list comprehension to print [1, 4, 9].",
        "hint": "Square each x inside a comprehension.",
        "validator": "script",
        "test_script": "grep -Eq 'squares[[:space:]]*=[[:space:]]*\\[x\\*x[[:space:]]+for[[:space:]]+x[[:space:]]+in[[:space:]]+nums\\]' answer.py && grep -Eq 'print\\(squares\\)' answer.py",
    },
    {
        "id": "21",
        "title": "Java: Entry point",
        "description": "Write Main.java so it contains a standard public static void main(String[] args) and prints ready.",
        "hint": "main is the entry point.",
        "validator": "script",
        "test_script": "grep -Eq 'public[[:space:]]+static[[:space:]]+void[[:space:]]+main\\(String\\[\\][[:space:]]+args\\)' Main.java && grep -Eq 'System\\.out\\.println\\(\\\"ready\\\"\\);' Main.java",
    },
    {
        "id": "22",
        "title": "JavaScript: Strict equality",
        "description": "Write answer.js so it compares left and right with strict equality and prints true when they match.",
        "hint": "Use three equals signs.",
        "validator": "script",
        "test_script": "grep -Eq '===' answer.js && grep -Eq 'console\\.log\\(true\\)' answer.js",
    },
    {
        "id": "23",
        "title": "Web security: SQL injection",
        "description": "Write answer.sh so it accepts only usernames from the allowlist alice, bob, or carol and prints ACCEPT when matched.",
        "hint": "Known-good inputs only.",
        "validator": "script",
        "test_script": "printf 'alice\n' | sh answer.sh | grep -xq 'ACCEPT' && printf 'mallory\n' | sh answer.sh | grep -xq 'REJECT'",
    },
    {
        "id": "24",
        "title": "Reverse engineering: Strings",
        "description": "Write answer.sh so it uses strings on the input binary and prints any line containing FLAG.",
        "hint": "Extract printable text first.",
        "validator": "script",
        "test_script": "printf 'abc\0FLAG{reverse_me}\0xyz' > sample.bin && sh answer.sh sample.bin | grep -xq 'FLAG{reverse_me}'",
    },
    {
        "id": "25",
        "title": "Digital forensics: Hashing",
        "description": "Write answer.sh so it prints the SHA-256 checksum of evidence.bin.",
        "hint": "Use a checksum command from coreutils.",
        "validator": "script",
        "test_script": "printf 'forensic data\n' > evidence.bin && expected=$(sha256sum evidence.bin | awk '{print $1}') && sh answer.sh evidence.bin | grep -xq \"$expected\"",
    },
    {
        "id": "26",
        "title": "Cryptography: Encoding",
        "description": "Write answer.sh so it base64-decodes encoded.txt and prints the plaintext.",
        "hint": "The encoding is reversible.",
        "validator": "script",
        "test_script": "printf 'SGVsbG8=\n' > encoded.txt && sh answer.sh encoded.txt | grep -xq 'Hello'",
    },
    {
        "id": "27",
        "title": "Secure coding: Input validation",
        "description": "Write answer.sh so it only accepts usernames matching ^[a-z][a-z0-9_]*$ and rejects anything else.",
        "hint": "Validate input before using it.",
        "validator": "script",
        "test_script": "printf 'alice1\n' | sh answer.sh | grep -xq 'VALID' && printf 'Bad-Name\n' | sh answer.sh | grep -xq 'INVALID'",
    },
    {
        "id": "28",
        "title": "CTF beginner: File signature",
        "description": "Write answer.sh so it reports the file type of the input using the file command.",
        "hint": "Magic bytes reveal the type.",
        "validator": "script",
        "test_script": "printf 'hello world\n' > note.txt && sh answer.sh note.txt | grep -qi 'text'",
    },
    {
        "id": "29",
        "title": "Docker: Run container",
        "description": "Write answer.sh so it prints the exact command to run an interactive Ubuntu container and remove it on exit.",
        "hint": "Combine --rm and -it.",
        "validator": "script",
        "test_script": "sh answer.sh | grep -xq 'docker run --rm -it ubuntu'",
    },
    {
        "id": "30",
        "title": "Git: Branch creation",
        "description": "Write answer.sh so it initializes a repo and creates a new branch named feature/auth.",
        "hint": "Use git checkout -b.",
        "validator": "script",
        "test_script": "git init -q && sh answer.sh && git branch --show-current | grep -xq 'feature/auth'",
    },
    {
        "id": "31",
        "title": "CI/CD: GitHub Actions trigger",
        "description": "Write .github/workflows/ci.yml so the workflow triggers on push.",
        "hint": "The trigger key is short.",
        "validator": "script",
        "test_script": "mkdir -p .github/workflows && grep -Eq '^on:' .github/workflows/ci.yml && grep -Eq 'push' .github/workflows/ci.yml",
    },
    {
        "id": "32",
        "title": "Cloud fundamentals: Shared model",
        "description": "Write answer.sh so it prints IaaS when the prompt describes provider-managed hardware and customer-managed VMs.",
        "hint": "The answer is an acronym.",
        "validator": "script",
        "test_script": "printf 'provider hardware and virtual machines\n' | sh answer.sh | grep -xq 'IaaS'",
    },
]

PUZZLE_METADATA = {
    "1": {"category": "Linux", "difficulty": "easy", "tags": ["linux", "filesystem", "cli"]},
    "2": {"category": "Programming", "difficulty": "easy", "tags": ["c", "build", "gcc"]},
    "3": {"category": "Linux", "difficulty": "easy", "tags": ["linux", "find", "filesystem"]},
    "4": {"category": "Linux", "difficulty": "easy", "tags": ["linux", "permissions", "filesystem"]},
    "5": {"category": "Programming", "difficulty": "easy", "tags": ["c", "stdio", "compile"]},
    "6": {"category": "Linux", "difficulty": "easy", "tags": ["linux", "navigation", "shell"]},
    "7": {"category": "Linux", "difficulty": "easy", "tags": ["linux", "process", "ps"]},
    "8": {"category": "Linux", "difficulty": "easy", "tags": ["linux", "networking", "sockets"]},
    "9": {"category": "Linux", "difficulty": "easy", "tags": ["linux", "packages", "apt"]},
    "10": {"category": "Linux", "difficulty": "easy", "tags": ["linux", "bash", "loops"]},
    "11": {"category": "Linux", "difficulty": "medium", "tags": ["linux", "permissions", "ownership"]},
    "12": {"category": "Linux", "difficulty": "easy", "tags": ["linux", "logs", "systemd"]},
    "13": {"category": "Linux", "difficulty": "easy", "tags": ["linux", "disk", "df"]},
    "14": {"category": "Linux", "difficulty": "medium", "tags": ["bash", "scripting", "files"]},
    "15": {"category": "Linux", "difficulty": "medium", "tags": ["bash", "filtering", "grep"]},
    "16": {"category": "Programming", "difficulty": "medium", "tags": ["c", "pointers", "memory"]},
    "17": {"category": "Programming", "difficulty": "medium", "tags": ["c", "malloc", "free"]},
    "18": {"category": "Programming", "difficulty": "medium", "tags": ["c", "structs", "linked-lists"]},
    "19": {"category": "Programming", "difficulty": "medium", "tags": ["c", "algorithms", "binary-search"]},
    "20": {"category": "Programming", "difficulty": "medium", "tags": ["python", "comprehensions", "lists"]},
    "21": {"category": "Programming", "difficulty": "easy", "tags": ["java", "entry-point", "syntax"]},
    "22": {"category": "Programming", "difficulty": "easy", "tags": ["javascript", "operators", "equality"]},
    "23": {"category": "Cybersecurity", "difficulty": "medium", "tags": ["web-security", "allowlist", "input-validation"]},
    "24": {"category": "Cybersecurity", "difficulty": "medium", "tags": ["reverse-engineering", "strings", "binary"]},
    "25": {"category": "Cybersecurity", "difficulty": "easy", "tags": ["forensics", "hashing", "sha256"]},
    "26": {"category": "Cybersecurity", "difficulty": "easy", "tags": ["cryptography", "base64", "encoding"]},
    "27": {"category": "Cybersecurity", "difficulty": "medium", "tags": ["secure-coding", "validation", "regex"]},
    "28": {"category": "Cybersecurity", "difficulty": "easy", "tags": ["ctf", "file-signatures", "file"]},
    "29": {"category": "DevOps", "difficulty": "easy", "tags": ["docker", "containers", "cli"]},
    "30": {"category": "DevOps", "difficulty": "easy", "tags": ["git", "branches", "workflow"]},
    "31": {"category": "DevOps", "difficulty": "easy", "tags": ["ci-cd", "github-actions", "yaml"]},
    "32": {"category": "DevOps", "difficulty": "easy", "tags": ["cloud", "iaas", "fundamentals"]},
}

for puzzle in PUZZLES:
    puzzle.update(PUZZLE_METADATA.get(puzzle["id"], {}))

def get_puzzle(pid):
    return next((p for p in PUZZLES if p["id"] == pid), None)


def response(ok=True, **kwargs):
    return jsonify({"ok": ok, **kwargs})


@app.route("/", methods=["GET"])
def index():
    return response(service="puzzle-server", time=datetime.now().isoformat())


@app.route("/health", methods=["GET"])
def health():
    return response(service="ok")


@app.route("/levels", methods=["GET"])
def levels():
    return jsonify([
        {
            "id": p["id"],
            "title": p["title"],
            "category": p["category"],
            "difficulty": p["difficulty"],
            "tags": p["tags"],
        }
        for p in PUZZLES
    ])


@app.route("/level/<pid>", methods=["GET"])
def level(pid):
    p = get_puzzle(pid)
    if not p:
        return response(False, error="not found"), 404

    return jsonify({
        "id": p["id"],
        "title": p["title"],
        "description": p["description"],
        "hint": p["hint"],
        "validator": p.get("validator", "equals"),
        "category": p["category"],
        "difficulty": p["difficulty"],
        "tags": p["tags"],
    })


@app.route("/submit", methods=["POST"])
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



def run_docker(files, script):
    tmp = tempfile.mkdtemp(prefix="puzzle_")

    try:
        for name, content in files.items():
            path = os.path.join(tmp, os.path.basename(name))
            with open(path, "w") as f:
                f.write(content)

        runner = os.path.join(tmp, "run.sh")
        with open(runner, "w") as f:
            f.write("#!/bin/sh\nset -e\n")
            f.write(script + "\n")

        os.chmod(runner, 0o700)

        cmd = [
            "docker", "run", "--rm",
            "-v", f"{tmp}:/work:ro",
            "-w", "/work",
            "--network", "none",
            "--memory", "256m",
            "--cpus", "0.5",
            "gcc:12",
            "/bin/sh", "-c", "./run.sh"
        ]

        proc = subprocess.run(cmd, capture_output=True, timeout=15)

        return {
            "passed": proc.returncode == 0,
            "exit_code": proc.returncode,
            "stdout": proc.stdout.decode(errors="ignore"),
            "stderr": proc.stderr.decode(errors="ignore"),
        }

    except subprocess.TimeoutExpired:
        return {"passed": False, "error": "timeout"}

    finally:
        shutil.rmtree(tmp, ignore_errors=True)



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
