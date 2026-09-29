# FAQ

## What is Lux?

Lux is an open-source puzzle and learning platform. It includes a Flask server, a web UI,
and a CLI agent that can ask a local Ollama model for contextual hints.

## What do I need before running Lux?

You need Python 3.10 or newer. Docker is required for script-based puzzles, and Ollama is
required if you want AI-generated hints from the CLI agent.

## Do I need Ollama to use the project?

Ollama is needed for the CLI hint flow. You can still inspect the code, run tests, and work
on many web, API, documentation, and tooling issues without using the hint model.

## Which model should I use?

The default examples use `llama3.2`. You can choose another local model with
`LUX_OLLAMA_MODEL` or provide a comma-separated fallback list with `LUX_OLLAMA_MODELS`.

## How do I start the server?

Install dependencies, start Ollama if you need hints, then run:

```bash
python3 server.py
```

The web UI is available at `http://127.0.0.1:5050/web`.

## How do I run the CLI agent?

Start the server first, then run:

```bash
python3 agent.py
```

The agent lists available levels, accepts attempts, and records solved progress locally.

## Where is CLI progress stored?

By default, progress is stored at `~/.lux/state.json`. You can override this path with the
`LUX_STATE` environment variable.

## How do I run tests?

Run the test suite from the repository root:

```bash
PYTHONPATH=. pytest -q
```

## Where can I find API and deployment details?

See `docs/API.md` for API routes and `docs/DEPLOYMENT.md` for deployment notes.
