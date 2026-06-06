# Interactive Puzzle Server + Agent

## Overview

- A minimal Flask-based puzzle server exposing simple levels and a validation endpoint.
- An interactive CLI agent that lists levels, fetches descriptions, accepts attempts, and asks Ollama for hints.

## Setup

1. Ensure you have Python 3.10+ and a running Ollama service with model `llama3.2` available locally.
2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run

1. Start the server:

```bash
python server.py
```

1. In another terminal, run the agent:

```bash
python agent.py
```

## Notes and security

- Some levels validate by string comparison.
- Script-based levels run inside a Docker container with network disabled, dropped capabilities, and limited CPU/memory.
- Docker must be installed, the daemon must be running, and the user running the server must be allowed to run `docker`.
- For production, use stronger sandboxing, authentication, and persistent progress storage.

## Design

- The server exposes `/levels`, `/level/<id>`, and `/submit`.
- For script-based levels, `POST /submit` accepts JSON `{ "level_id": "5", "files": { "answer.c": "<source>" } }` and returns test output.
- The agent uses Ollama (`llama3.2`) to produce contextual hints; it instructs the model not to reveal flags.

## Next steps

- Add more levels with staged tasks and progressive hints.
- Implement an interactive web UI.
- Add secure sandbox execution for C compilation and run (via Firecracker, gVisor, or chrooted containers).
