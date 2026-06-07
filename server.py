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
