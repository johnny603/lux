# Interactive Puzzle Server + Agent

![CI](https://github.com/johnny603/lux/actions/workflows/ci.yml/badge.svg)

![CodeQL](https://github.com/johnny603/lux/actions/workflows/codeql.yml/badge.svg)

## Overview

- A minimal Flask-based puzzle server exposing simple levels and a validation endpoint.
- An interactive CLI agent that lists levels, fetches descriptions, accepts attempts, and asks Ollama for hints.

## Setup

- Python 3.10+
- Docker installed and running (required for script-based puzzles)
- Ollama installed and running locally
- Model llama3.2 pulled

It is recomended to use a virtual environment
```
python3 -m venv venv
source venv/bin/activate
```

1. Install dependencies:

```
python3 -m pip install -r requirements.txt
```

## Run
2. Start Ollama service
```
ollama serve
ollama pull llama3.2
ollama list
```

3. Start the server:

```
python3 server.py
```

4. In another terminal, run the agent:

```
python3 agent.py
```
Server is hosted in http://127.0.0.1:5050

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
