# Lux Roadmap

> Long-term vision: Build Lux into a puzzle-based learning platform that combines Linux, programming, cybersecurity, and AI-assisted learning with a modern cross-platform experience.
>
> Roadmap status: the community milestone, sandbox hardening, and v1.0 release artifacts are complete. The current implementation centers on server.py and agent.py, with local JSON state and a Flutter/Dart path planned for mobile support.

If you want to work on a section of the roadmap
Get my approval and format the branch like this:
`<username>/<scope>/<feature>`

## Development

Create and activate a virtual environment, then install the application dependencies:

```bash
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

Start the development server:

```bash
python server.py
```

The server listens on `http://127.0.0.1:5050`. Flask's development command can also be used:

```bash
export FLASK_APP=server.py
export FLASK_DEBUG=1
flask run --port 5050
```

Run the test suite and, when installed, lint the project:

```bash
pytest
ruff check .
```

Docker is required for script-based puzzle validation. Ollama is optional for AI hints.

## Production

Copy `.env.example` to `.env`, replace all placeholder secrets, and start the container stack:

```bash
docker-compose up -d
```

The application is served by Gunicorn on port `5050`. Check liveness and readiness with:

```bash
curl http://127.0.0.1:5050/health
curl http://127.0.0.1:5050/ready
```

Use `.env.example` as the configuration reference. `LUX_DOCKER_RUNTIME=runsc` enables gVisor where installed, and `LUX_SANDBOX_AUDIT_LOG` selects the JSONL audit destination. Single-instance deployments can use SQLite; PostgreSQL is recommended for hosted deployments. The current local-first code still stores progress in JSON, so database migrations and repository integration are required before enabling multi-user production persistence.

Before a public launch, complete authentication, password and token security, database migrations, TLS, rate limiting, upload limits, backups, monitoring, and authorization checks. See [docs/DEPLOYMENT.md](DEPLOYMENT.md) for the deployment checklist and Gunicorn configuration.

## Core Platform

* [x] Flask puzzle server
* [x] CLI puzzle agent
* [x] Ollama-powered hints
* [x] Docker-based code validation
* [x] GitHub Actions CI
* [x] Security scanning (Bandit, CodeQL, Snyk)

## Puzzle Content

### Linux

* [x] Basic Linux command puzzles
* [x] File system navigation
* [x] Process management
* [x] Networking
* [x] Package management
* [x] Shell scripting
* [x] Permissions and ownership
* [x] Log analysis
* [x] System administration
* [x] Bash challenge levels

### Programming

* [x] Basic C challenges
* [x] Intermediate C puzzles
* [x] Memory management challenges
* [x] Data structures
* [x] Algorithms
* [x] Python puzzles
* [x] Java puzzles
* [x] JavaScript puzzles

### Cybersecurity

* [x] Web security puzzles
* [x] Reverse engineering
* [x] Digital forensics
* [x] Cryptography
* [x] Secure coding challenges
* [x] Beginner CTF-style levels

### DevOps

* [x] Docker puzzles
* [x] Git challenges
* [x] CI/CD exercises
* [x] Cloud fundamentals

### Current Puzzle Catalog

* Linux command, scripting, and admin levels are implemented
* Programming levels cover C, Python, Java, and JavaScript
* Cybersecurity levels cover web security, reverse engineering, forensics, cryptography, secure coding, and beginner CTFs
* DevOps levels cover Docker, Git, CI/CD, and cloud fundamentals
* Each puzzle includes category, difficulty, and tags metadata for filtering

## User Experience

### CLI Improvements

* [x] Progress tracking in agent.py with per-level completion, streaks, and solved-history summaries
* [x] Achievement system with unlockable milestones and badge summaries tied to completed levels
* [x] Save/load progress using JSON state files so the CLI can restore solved levels and user state
* [x] Difficulty ratings from server.py surfaced in the CLI and used for puzzle ordering
* [x] Better hint generation in agent.py tuned to the current puzzle, progress, and prior attempts

Note: These CLI progress and achievement features are now implemented in the main codebase with backward-compatible state migration.

### Web UI

* [x] Flask web frontend layered on top of server.py as the primary browser-based experience
* [x] Responsive design for desktop and mobile browsers
* [x] User profiles for saved progress, preferences, and personalization
* [x] Leaderboards for puzzle completion, streaks, and challenge performance
* [x] Puzzle browser with search, filters, categories, and difficulty views
* [x] Progress dashboard with completion, streak, and achievement summaries

### Mobile App

* [ ] Flutter/Dart prototype that reuses the same puzzle API exposed by server.py
* [ ] Shared API backend for authentication, progress sync, puzzle delivery, and submissions
* [ ] iOS support through the Flutter client
* [ ] Android support through the Flutter client
* [ ] Offline puzzle packs for limited-connectivity play
* [ ] Push notifications for streaks, reminders, and new content

## AI Features

* [x] Ollama hint generation
* [x] Adaptive hints based on progress and puzzle history in agent.py
* [x] Multiple AI models with a clear fallback order
* [x] Local model selection for privacy and offline use
* [x] Personalized learning paths based on strengths and gaps
* [x] Puzzle generation with AI for new practice content

## Security & Sandboxing

### Current

* [x] Docker execution
* [x] Resource limits
* [x] Network isolation

### Planned

* [x] Stronger Docker restrictions for safer puzzle execution
* [x] Read/write isolation for ephemeral workspace access
* [ ] gVisor support for a stronger runtime boundary
* [ ] Firecracker support for microVM-based isolation
* [x] Secure execution auditing for traceable sandbox activity

See [docs/FIRECRACKER.md](FIRECRACKER.md) for the microVM design and rollout criteria.

## Testing

* [x] Smoke tests
* [x] API integration tests
* [x] Docker execution tests
* [x] Security tests
* [x] End-to-end testing

## Open Source Community

* [x] Contributing guide
* [x] Issue templates
* [x] Pull request template
* [x] Contributor recognition system
* [x] Good first issue labels
* [x] Mentorship-friendly issues

Contributor data and starter issue guidance live in `contributors.json`, `.github/labels.yml`, and [docs/MENTORSHIP_ISSUES.md](MENTORSHIP_ISSUES.md).

## Game Vision

### Puzzle Adventure Mode

* [x] Story-driven progression
* [x] Unlockable worlds
* [x] Puzzle campaigns
* [x] Character progression
* [x] Achievement badges
* [x] Certain puzzles are certain building blocks to advance

### Running / Puzzle Hybrid

* [x] Level builder
* [x] Real-world activity integration
* [x] Daily puzzle challenges
* [x] XP and leveling system
* [x] Streak tracking
* [x] Exploration-based gameplay
* [x] Mobile-first experience

## Release Goals

### v0.1

* [x] Stable CLI experience
* [x] 25+ puzzles
* [x] Improved testing

### v0.5

* [x] Web UI
* [x] User accounts
* [x] 100+ puzzles

### v1.0

* [ ] Flutter mobile app
* [x] Story mode
* [x] Advanced sandboxing
* [x] Release artifacts: Dockerfile, Compose, deployment documentation, API documentation, `/ready`, and versioned submit endpoint
* [ ] Public launch
