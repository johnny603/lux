# Interactive Puzzle Server + Agent

![CI (main)](https://github.com/johnny603/lux/actions/workflows/ci.yml/badge.svg) ![CI (achievements)](https://github.com/johnny603/lux/actions/workflows/ci.yml/badge.svg?branch=roadmap/achievements) ![CodeQL](https://github.com/johnny603/lux/actions/workflows/codeql.yml/badge.svg)

## Overview

- A minimal Flask-based puzzle server exposing simple levels and a validation endpoint.
- An interactive CLI agent that lists levels, fetches descriptions, accepts attempts, and asks Ollama for hints.
- A lightweight Flask web UI with puzzle browsing, filtering, progress tracking, and puzzle detail pages.
- Versioned API routes under `/api/v1/...` for puzzle discovery, progress, achievements, and future clients.

## Setup

- Python 3.10+
- Docker installed and running (required for script-based puzzles)
- Ollama installed and running locally
- Model llama3.2 pulled, or another local model selected through `LUX_OLLAMA_MODEL` / `LUX_OLLAMA_MODELS`

It is recommended to use a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

## Run

1. Install dependencies:

   ```bash
   python3 -m pip install -r requirements.txt
   ```

2. Start Ollama service:

   ```bash
   ollama serve
   ollama pull llama3.2
   ollama list
   ```

3. Start the server:

   ```bash
   python3 server.py
   ```

4. In another terminal, run the agent:


   ```bash
   python3 agent.py
   ```

   Server is hosted at [http://127.0.0.1:5050](http://127.0.0.1:5050).

5. Open the web UI in a browser:

   ```bash
   http://127.0.0.1:5050/web
   ```

Optional API endpoints:

- `/api/v1/levels`
- `/api/v1/level/<id>`
- `/api/v1/progress`
- `/api/v1/achievements`

## CLI Usage & State

The interactive CLI agent stores user progress locally in a JSON state file. By default the state file is located at `~/.lux/state.json`.

Environment variable `LUX_STATE` can override the path to the state file. Example:

```bash
export LUX_STATE=/tmp/lux-state.json
python3 agent.py
```

When you solve a level using the CLI the agent will persist solved history and unlocked achievements to the state file. You can inspect it with:

```bash
cat ~/.lux/state.json
```

Sample run (quick):

1. Start the server: `python3 server.py`
2. Run the agent: `python3 agent.py`
3. Choose a level id and attempt it. When marked correct, the CLI prints a confirmation and any newly unlocked achievements.
4. Restart the agent and note that solved levels and achievements are listed in the `Available levels` output.

If your CI badge for a branch shows failing, ensure you push the branch and open the PR so GitHub Actions can run; local tests can be run with:

```bash
PYTHONPATH=. pytest -q
```

## Notes and security

- Some levels validate by string comparison.
- Script-based levels run inside a Docker container with network disabled, dropped capabilities, and limited CPU/memory.
- Docker must be installed, the daemon must be running, and the user running the server must be allowed to run `docker`.
- For production, use stronger sandboxing, authentication, and persistent progress storage.

## Design

- The server exposes `/levels`, `/level/<id>`, and `/submit`.
- The server also exposes `/api/v1/levels`, `/api/v1/level/<id>`, `/api/v1/progress`, `/api/v1/achievements`, `/web`, `/dashboard`, and `/puzzles/<id>`.
- For script-based levels, `POST /submit` accepts JSON `{ "level_id": "5", "files": { "answer.c": "<source>" } }` and returns test output.
- The agent uses Ollama (`llama3.2`) to produce contextual hints; it instructs the model not to reveal flags.
- Hint models can be configured with `LUX_OLLAMA_MODEL` for a preferred local model and `LUX_OLLAMA_MODELS` for a comma-separated fallback list.

## Current Puzzle Catalog

- Linux: command-line navigation, process management, networking, package management, shell scripting, permissions, logs, system administration, and Bash levels
- Programming: C pointers, memory management, data structures, algorithms, Python comprehensions, Java entry points, and JavaScript equality
- Cybersecurity: web security, reverse engineering, digital forensics, cryptography, secure coding, and beginner CTF-style levels
- DevOps: Docker, Git, CI/CD, and cloud fundamentals
- Every puzzle includes `category`, `difficulty`, and `tags` metadata for filtering in the agent and future UI work

## Next steps

- Add more levels with staged tasks and progressive hints.
- Implement an interactive web UI.
- Add secure sandbox execution for C compilation and run (via Firecracker, gVisor, or chrooted containers).
