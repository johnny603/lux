# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Pre-commit configuration for automated code quality and formatting checks ([#26](https://github.com/johnny603/lux/pull/26)).
- Dedicated CI helper script `scripts/ci.sh` for testing, linting, and building ([#24](https://github.com/johnny603/lux/pull/24)).
- Community health files and security policy documentation ([#23](https://github.com/johnny603/lux/pull/23), [#56](https://github.com/johnny603/lux/pull/56)).
- EditorConfig configuration for cross-editor consistency ([#57](https://github.com/johnny603/lux/pull/57)).
- Snyk workflow guard ensuring the action does not fail when `SNYK_TOKEN` is unset ([#23](https://github.com/johnny603/lux/pull/23)).

### Changed
- Tightened Bandit scan scope and severity threshold for faster local CI cycles ([#24](https://github.com/johnny603/lux/pull/24)).
- Bumped `ruff` dependency requirement to `>=0.16.5` ([#32](https://github.com/johnny603/lux/pull/32)).
- Bumped `gunicorn` dependency requirement to `>=26.2.0` ([#31](https://github.com/johnny603/lux/pull/31)).
- Enhanced README with project description and community links ([#47](https://github.com/johnny603/lux/pull/47), [#55](https://github.com/johnny603/lux/pull/55)).

### Fixed
- Snyk security job failure when running on external PRs or without secrets ([#23](https://github.com/johnny603/lux/pull/23)).
- Resolved lint and format violations across Python codebase ([#22](https://github.com/johnny603/lux/pull/22)).

## [0.1.0] - 2026-06-06

### Added
- Initial public release of Lux escape room game and REST API.
- Core room mechanics, puzzle validation logic, and CLI runner.
- REST API service endpoints under `/api/v1/...`.
- Basic web UI and puzzle assets.
