# Lux Roadmap

> Long-term vision: Build Lux into a puzzle-based learning platform that combines Linux, programming, cybersecurity, and AI-assisted learning with a modern cross-platform experience.
>
> Roadmap status: current implementation centers on server.py and agent.py, with JSON state for progress and a Flutter/Dart path planned for mobile support.

If you want to work on a section of the roadmap
Get my approval and format the branch like this:
<username>/<scope>/<feature>


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
* [ ] User profiles for saved progress, preferences, and personalization
* [ ] Leaderboards for puzzle completion, streaks, and challenge performance
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
* [ ] Personalized learning paths based on strengths and gaps
* [ ] Puzzle generation with AI for new practice content

## Security & Sandboxing

### Current

* [x] Docker execution
* [x] Resource limits
* [x] Network isolation

### Planned

* [x] Stronger Docker restrictions for safer puzzle execution
* [x] Read/write isolation for ephemeral workspace access
* [ ] User namespace isolation for reduced host exposure
* [ ] gVisor support for a stronger runtime boundary
* [ ] Firecracker support for microVM-based isolation
* [ ] Secure execution auditing for traceable sandbox activity

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
* [ ] Contributor recognition system
* [ ] Good first issue labels
* [ ] Mentorship-friendly issues

## Game Vision

### Puzzle Adventure Mode

* [ ] Story-driven progression
* [ ] Unlockable worlds
* [ ] Puzzle campaigns
* [ ] Character progression
* [ ] Achievement badges

### Running / Puzzle Hybrid

* [ ] Real-world activity integration
* [ ] Daily puzzle challenges
* [ ] XP and leveling system
* [ ] Streak tracking
* [ ] Exploration-based gameplay
* [ ] Mobile-first experience

## Release Goals

### v0.1

* [ ] Stable CLI experience
* [ ] 25+ puzzles
* [ ] Improved testing

### v0.5

* [ ] Web UI
* [ ] User accounts
* [ ] 100+ puzzles

### v1.0

* [ ] Flutter mobile app
* [ ] Story mode
* [ ] Advanced sandboxing
* [ ] Public launch
