from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# Simple in-memory puzzle definitions. Each puzzle has:
# - id, title, description, hint, flag (expected answer)
puzzles = [
  {
    "id": "1",
    "title": "Linux: List hidden files",
    "description": (
      "In a directory you need to list all files, including hidden ones. "
      "What `ls` command option will show hidden files? Provide the single flag or full command."
    ),
    "hint": "Try an `ls` option that starts with a dot-aware flag.",
    "flag": "-a",
  },
  {
    "id": "2",
    "title": "C: Simple compilation",
    "description": (
      "You have a C source file `hello.c`. What sequence of commands compiles it into an executable `hello`? "
      "Answer with the gcc command used."
    ),
    "hint": "Use `gcc` to compile `hello.c` into `hello`.",
    "flag": "gcc hello.c -o hello",
  },
  {
    "id": "3",
    "title": "Linux: Find large files",
    "description": (
      "Find files larger than 1 megabyte in the current directory. "
      "Provide the `find` command flags (e.g. `-size +1M`) or full command that would locate them."
    ),
    "hint": "`find` supports `-size` with + for greater-than and M for megabytes.",
    "validator": "contains",
    "flag": "-size +1M",
  },
  {
    "id": "4",
    "title": "Linux: File permissions",
    "description": (
      "There's a file that only the owner can read and write. What `chmod` symbolic mode would set permissions to `rw- r-- r--`? "
    ),
    "hint": "Owner needs read/write, group and others need read only; think of symbolic or octal modes.",
    "validator": "equals",
    "flag": "chmod 644 <file>",
  },
  {
    "id": "5",
    "title": "C: Print 42",
    "description": (
      "Write a C program `answer.c` that prints the number `42` followed by a newline to stdout. "
      "Submit the source file; the server will compile and run it to verify output."
    ),
    "hint": "Use `printf` in `main()` and return 0.",
    "validator": "script",
    "test_script": "gcc answer.c -o answer && ./answer | grep -xq '42'",
  },
  {
    "id": "6",
    "title": "C: Sum two numbers",
    "description": (
      "Write a C program `sum.c` that reads two integers from stdin and prints their sum. "
      "The tester will provide input `2 3` and expect `5` on stdout."
    ),
    "hint": "Use `scanf` to read two ints and `printf` their sum.",
    "validator": "script",
    "test_script": "gcc sum.c -o sum && printf '2 3' | ./sum | grep -xq '5'",
  },
  {
    "id": "7",
    "title": "Linux: Grep for pattern",
    "description": (
      "Given a file `log.txt`, produce a `grep` command that finds lines containing the word `ERROR` (case-sensitive)."
    ),
    "hint": "Use `grep` with the simple pattern `ERROR`.",
    "validator": "contains",
    "flag": "grep ERROR",
  },
  {
    "id": "8",
    "title": "C: Reverse a string",
    "description": (
      "Write a C program `reverse.c` that reads one word from stdin and prints it reversed with a newline. "
      "The checker will test with input `kite` and expect `etik`."
    ),
    "hint": "Read a string into a buffer, then print characters from the end back to the start.",
    "validator": "script",
    "test_script": "gcc reverse.c -o reverse && printf 'kite' | ./reverse | grep -xq 'etik'",
  },
]


@app.route("/", methods=["GET"]) 
def index():
  return jsonify({"service": "puzzle-server", "time": datetime.now().isoformat()})


@app.route("/levels", methods=["GET"])
def list_levels():
  # Return brief metadata for all puzzles
  return jsonify([{"id": p["id"], "title": p["title"]} for p in puzzles])


@app.route("/level/<level_id>", methods=["GET"])
def get_level(level_id):
  for p in puzzles:
    if p["id"] == level_id:
      # expose validator so clients can know whether to submit files
      rv = {k: p[k] for k in ("id", "title", "description", "hint")}
      if "validator" in p:
        rv["validator"] = p["validator"]
      return jsonify(rv)
  return jsonify({"error": "level not found"}), 404


@app.route("/submit", methods=["POST"])
def submit():
  data = request.json or {}
  level_id = str(data.get("level_id"))
  attempt = (data.get("attempt") or "").strip()
  files = data.get("files") or {}
  if not level_id:
    return jsonify({"ok": False, "error": "missing level_id"}), 400
  for p in puzzles:
    if p["id"] == level_id:
      return validate_submission(p, attempt, files)
  return jsonify({"ok": False, "error": "level not found"}), 404


def validate_submission(puzzle: dict, attempt: str, files: dict):
  validator = puzzle.get("validator", "equals")
  if validator == "equals":
    correct = attempt == puzzle.get("flag")
    return jsonify({"ok": True, "correct": correct, "expected": (puzzle.get("flag") if not correct else None)})
  if validator == "contains":
    correct = puzzle.get("flag") in attempt
    return jsonify({"ok": True, "correct": correct, "expected": (puzzle.get("flag") if not correct else None)})
  if validator == "script":
    test_script = puzzle.get("test_script")
    if not test_script:
      return jsonify({"ok": False, "error": "no test script configured"}), 500
    try:
      out = run_in_docker(files, test_script)
      return jsonify({"ok": True, "correct": out.get("passed"), "output": out})
    except Exception as e:
      return jsonify({"ok": False, "error": str(e)}), 500
  return jsonify({"ok": False, "error": "unsupported validator"}), 400


def run_in_docker(files: dict, test_script: str) -> dict:
  """Create a temporary workspace, write files, and run the test script inside a restricted Docker container.

  Requires Docker CLI available on the host. The function returns a dict with keys:
  - passed: bool
  - exit_code: int
  - stdout: str
  - stderr: str
  - timed_out: bool
  """
  import tempfile
  import os
  import shutil
  import subprocess

  tmpdir = tempfile.mkdtemp(prefix="puzzle_")
  try:
    # write files
    for fname, content in files.items():
      safe_path = os.path.join(tmpdir, os.path.basename(fname))
      with open(safe_path, "w") as f:
        f.write(content)
    # write runner script
    runner = os.path.join(tmpdir, "run.sh")
    with open(runner, "w") as f:
      f.write("#!/bin/sh\nset -euo pipefail\n")
      f.write(test_script + "\n")
    os.chmod(runner, 0o700)

    # docker command
    cmd = [
      "docker", "run", "--rm",
      "-v", f"{tmpdir}:/work:ro",  # mount read-only
      "-w", "/work",
      "--network", "none",
      "--pids-limit", "64",
      "--cpus", "0.5",
      "--memory", "256m",
      "--security-opt", "no-new-privileges",
      "--cap-drop", "ALL",
      "gcc:12",
      "/bin/sh", "-c", "./run.sh"
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)
    passed = proc.returncode == 0
    return {
      "passed": passed,
      "exit_code": proc.returncode,
      "stdout": proc.stdout.decode(errors="replace"),
      "stderr": proc.stderr.decode(errors="replace"),
      "timed_out": False,
    }
  except subprocess.TimeoutExpired:
    return {"passed": False, "exit_code": None, "stdout": "", "stderr": "timeout", "timed_out": True}
  finally:
    try:
      shutil.rmtree(tmpdir)
    except Exception:
      pass


if __name__ == "__main__":
  # Run dev server. For production use a proper WSGI server and sandboxing for execution.
  app.run(host="127.0.0.1", port=5050, debug=False, use_reloader=False)
