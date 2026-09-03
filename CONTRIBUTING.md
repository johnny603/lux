# Contributing to Lux

Thank you for your interest in contributing to Lux!

Lux is an open-source puzzle platform featuring:

* A Flask-based puzzle server
* A CLI agent for solving puzzles
* Ollama-powered contextual hints
* Docker-based validation for code challenges
* Automated testing, linting, and security scanning

We welcome bug fixes, new puzzles, documentation improvements, tests, and new features.

## Contributor Recognition

Lux maintains a checked-in `contributors.json` manifest for people who contribute code, puzzles, documentation, security improvements, or mentorship. Maintainers should update it through a reviewed pull request. Available badges and four scoped starter issues are documented in `docs/MENTORSHIP_ISSUES.md`.

---

## Development Setup

### Prerequisites

* Python 3.10+
* Git
* Docker (for script-based puzzle validation)
* Ollama (optional, required for AI hints)

### Clone the Repository

```bash
git clone https://github.com/johnny603/lux.git
cd lux
```

### Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

Application dependencies:

```bash
pip install -r requirements.txt
```

Development dependencies:

```bash
pip install -r requirements-dev.txt
```

---

## Running the Project

### Start the Puzzle Server

```bash
python3 server.py
```

By default the server listens on:

```text
http://127.0.0.1:5050
```

### Start the Agent

In a separate terminal:

```bash
source venv/bin/activate
python3 agent.py
```

If using a custom server URL:

```bash
export PUZZLE_SERVER=http://127.0.0.1:5050
python3 agent.py
```

### Ollama Setup (Optional)

Install Ollama and ensure a model is available locally:

```bash
ollama pull llama3.2
ollama serve
```

The agent uses Ollama to generate hints while avoiding direct solutions.

---

## Testing

Run all tests:

```bash
pytest
```

Current tests are located in:

```text
tests/
```

When adding new functionality, please add tests when practical.

---

## Linting

Run Ruff:

```bash
ruff check .
```

Check formatting:

```bash
ruff format --check .
```

Auto-format:

```bash
ruff format .
```

---

## Security Checks

Run Bandit:

```bash
bandit -r .
```

Security checks are also performed automatically through:

* Bandit
* CodeQL
* Snyk
* Dependabot

---

## Pull Request Process

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Run:

```bash
ruff check .
pytest
bandit -r .
```

5. Commit using Conventional Commits.
6. Open a Pull Request.

---

## Conventional Commits

Please follow the Conventional Commits specification.

Examples:

```text
feat: add new puzzle category
fix: correct level validation logic
docs: update installation guide
test: add API smoke tests
refactor: simplify puzzle lookup
chore: update dependencies
ci: add CodeQL workflow
```

For breaking changes:

```text
feat!: redesign puzzle API
```

or

```text
feat(api): redesign puzzle API

BREAKING CHANGE: endpoint responses changed
```

---

## Areas for Contribution

Some ideas for contributors:

* Add new Linux puzzles
* Add new C programming puzzles
* Improve Docker sandboxing
* Add web UI support
* Add progress persistence
* Improve Ollama prompt engineering
* Expand automated test coverage
* Improve documentation

---

## Code Style

* Prefer clear, readable code.
* Keep functions focused and small.
* Add comments when behavior is non-obvious.
* Avoid unnecessary dependencies.
* Maintain compatibility with Python 3.10+.

---

## Reporting Issues

Before opening an issue:

* Search existing issues first.
* Include reproduction steps.
* Include relevant logs and screenshots.
* Provide environment information.

Use the provided issue templates whenever possible.

---

## Code of Conduct

Be respectful and constructive.

We welcome contributors of all experience levels and encourage collaboration, learning, and knowledge sharing.

Thank you for helping improve Lux!

