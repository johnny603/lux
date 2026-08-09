Changelog
---------

- Add achievements evaluator (`achievements.py`) with simple rules:
  - `first_solve` — solve your first puzzle
  - `solve_5`, `solve_10`, `solve_25` — milestone counts
  - category completion achievements when all puzzles in a category are solved
- Persist achievements in user state (`storage.py` now includes `achievements` in state model)
- CLI integration in `agent.py`: displays achievements summary, notifies on newly unlocked achievements
- CLI commands added: `ach` (list achievements) and `reset-ach` (clear unlocked achievements)

Testing Notes
-------------

- Unit tests added: `tests/test_achievements.py` for evaluator logic and `tests/test_cli_state.py` for state persistence.
- Run the test suite locally with:

```
PYTHONPATH=. pytest -q
```

- The changes are additive and backwards-compatible: existing state files without `achievements` are handled.

Reviewer Suggestions
--------------------

- Review `achievements.py` for additional rules or localization requirements.
- Confirm CLI UX for listing/resetting achievements is acceptable; consider adding a dedicated `--achievements` flag or subcommand for scriptability.
- Review state schema change in `storage.py` and ensure downstream consumers (if any) expect the `achievements` key.

Notes
-----

- Timestamps now use timezone-aware UTC formatting to avoid deprecation warnings.
- No external dependencies added.
