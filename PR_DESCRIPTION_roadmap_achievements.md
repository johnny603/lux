PR: https://github.com/johnny603/lux/pull/11

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
