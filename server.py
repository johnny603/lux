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
        "description": "What operator is used to dereference a pointer in C?",
        "hint": "It is the same symbol used for multiplication",
        "validator": "equals",
        "flag": "*",
    },
    {
        "id": "17",
        "title": "C: Memory management",
        "description": "Which C function releases memory allocated with malloc?",
        "hint": "You call it with the pointer variable",
        "validator": "equals",
        "flag": "free",
    },
    {
        "id": "18",
        "title": "C: Data structures",
        "description": "Which keyword defines a structure type in C?",
        "hint": "It starts many user-defined record types",
        "validator": "equals",
        "flag": "struct",
    },
    {
        "id": "19",
        "title": "C: Algorithms",
        "description": "What is the average-case time complexity of binary search on a sorted array?",
        "hint": "Think divide-and-conquer",
        "validator": "equals",
        "flag": "O(log n)",
    },
    {
        "id": "20",
        "title": "Python: List comprehension",
        "description": "Write a Python list comprehension that squares each number in nums.",
        "hint": "Use x*x for x in nums",
        "validator": "contains",
        "flag": "[x*x for x in nums]",
    },
    {
        "id": "21",
        "title": "Java: Entry point",
        "description": "What is the full Java method signature for the standard program entry point?",
        "hint": "public, static, void, main",
        "validator": "equals",
        "flag": "public static void main(String[] args)",
    },
    {
        "id": "22",
        "title": "JavaScript: Strict equality",
        "description": "Which operator checks strict equality in JavaScript?",
        "hint": "It has three symbols",
        "validator": "equals",
        "flag": "===",
    },
    {
        "id": "23",
        "title": "Web security: SQL injection",
        "description": "Name one defensive technique that prevents SQL injection.",
        "hint": "Do not concatenate untrusted input into queries",
        "validator": "contains",
        "flag": "parameterized",
    },
    {
        "id": "24",
        "title": "Reverse engineering: Strings",
        "description": "Which Linux command prints printable strings found in a binary file?",
        "hint": "The command name matches the output",
        "validator": "equals",
        "flag": "strings",
    },
    {
        "id": "25",
        "title": "Digital forensics: Hashing",
        "description": "Which command computes a SHA-256 hash for evidence.bin?",
        "hint": "Use a GNU coreutils checksum command",
        "validator": "equals",
        "flag": "sha256sum evidence.bin",
    },
    {
        "id": "26",
        "title": "Cryptography: Encoding",
        "description": "Decode SGVsbG8= and submit the plaintext.",
        "hint": "This is base64",
        "validator": "equals",
        "flag": "Hello",
    },
    {
        "id": "27",
        "title": "Secure coding: Input validation",
        "description": "Which concept means only known-good input formats are accepted?",
        "hint": "The opposite of denylisting",
        "validator": "contains",
        "flag": "allowlist",
    },
    {
        "id": "28",
        "title": "CTF beginner: File signature",
        "description": "Which command can identify file type information from magic bytes?",
        "hint": "It is a short, common Unix utility",
        "validator": "equals",
        "flag": "file",
    },
    {
        "id": "29",
        "title": "Docker: Run container",
        "description": "What command runs an interactive Ubuntu container and removes it when you exit?",
        "hint": "Combine -it and --rm",
        "validator": "equals",
        "flag": "docker run --rm -it ubuntu",
    },
    {
        "id": "30",
        "title": "Git: Branch creation",
        "description": "What command creates and switches to a new branch named feature/auth?",
        "hint": "Use checkout with -b",
        "validator": "equals",
        "flag": "git checkout -b feature/auth",
    },
    {
        "id": "31",
        "title": "CI/CD: GitHub Actions trigger",
        "description": "In GitHub Actions, which key in a workflow file defines trigger events?",
        "hint": "It is a short keyword",
        "validator": "equals",
        "flag": "on",
    },
    {
        "id": "32",
        "title": "Cloud fundamentals: Shared model",
        "description": "Which cloud model gives you virtual machines while the provider manages physical hardware?",
        "hint": "Infrastructure as a Service abbreviation",
        "validator": "equals",
        "flag": "IaaS",
    },
]

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
    return jsonify([{"id": p["id"], "title": p["title"]} for p in PUZZLES])


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
        "validator": p.get("validator", "equals")
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
