Roadmap/achievements

## Summary

This PR implements a lightweight achievements system and integrates it into the CLI agent. Key changes:

- Add `achievements.py`: evaluator with simple, declarative rules (first solve, milestone counts, and category completion).
- Persist unlocked achievements in the local JSON state (state model extended in `storage.py`).
- CLI integration in `agent.py`: shows achievements summary, notifies on newly unlocked achievements, and adds two commands:
  - `ach` / `achievements` — list unlocked achievements
  - `reset-ach` / `reset-achievements` — clear unlocked achievements (confirmation required)
- Use timezone-aware UTC timestamps to avoid deprecation warnings.
- Add unit tests for achievements and state persistence (`tests/test_achievements.py`, `tests/test_cli_state.py`).

## Type of Change

Select all that apply:

* [x] feat: New feature
* [ ] fix: Bug fix
* [x] docs: Documentation changes
* [x] test: New or updated tests
* [ ] refactor: Code restructuring without behavior changes
* [ ] chore: Maintenance, tooling, CI/CD, dependencies
* [ ] ci: GitHub Actions or automation changes

## Related Issue

Closes # (none)

## Testing

Local test summary:

- Ran full test suite locally: `PYTHONPATH=. pytest -q` — all tests passed (8 passed at time of commit).

Suggested verification commands:

```bash
PYTHONPATH=. pytest -q
ruff check .
bandit -r .
```

Manual CLI checks:

1. Start the server: `python3 server.py`
2. Start the agent: `python3 agent.py`
3. Solve a level to trigger achievements and observe messages in the CLI.
4. Use `ach` to list achievements and `reset-ach` to clear them.

## Checklist

* [x] My commit messages follow the Conventional Commits specification.
* [x] I have added or updated tests where appropriate.
* [x] I have updated documentation where appropriate.
* [ ] All CI checks pass. (Please verify on GitHub Actions.)
* [x] My changes do not introduce known security issues.

## Example Commit Messages

```text
feat: add achievements evaluator and CLI integration
test: add unit tests for achievements and storage
docs: update README with CLI usage and LUX_STATE info
fix: use timezone-aware timestamps
```

## Screenshots / Logs (Optional)

Attach screenshots or logs if relevant.

---

Paste this body into the GitHub PR description when creating the pull request, or use the file contents as the PR description.
