# Frequently Asked Questions (FAQ)

Answers to common questions and troubleshooting steps for setting up and developing Lux.

---

### Do I need Docker to run Lux?
Yes, Docker is required for running and validating script-based puzzles in an isolated environment. However, exploring the web UI (`/web`) and CLI hint interactions can run without Docker.

### Do I need Ollama?
Ollama is required for generating contextual hints in the interactive agent. If Ollama is not running locally, hint requests will return an error, but the rest of the application and validation remain operational.

### Where is my progress stored?
By default, the CLI agent persists solved levels and achievements to `~/.lux/state.json`. You can customize or override this location by setting the `LUX_STATE` environment variable (for example, `export LUX_STATE=/tmp/lux-state.json`).

### Why does `python3 server.py` fail on port 5050?
Port 5050 is already bound by another running process. You can terminate the existing process or run the server on a different port.

### How do I run just the tests for one module?
Run `pytest` followed by the specific test path, for example:
```bash
pytest tests/test_web_api.py
```

### Why does CI fail on my PR for whitespace or formatting?
The repository enforces code style and formatting standards via pre-commit hooks. Check `.pre-commit-config.yaml` and run pre-commit locally before pushing:
```bash
pre-commit run --all-files
```
