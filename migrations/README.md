# Database migrations

This directory is reserved for the database-backed progress and authentication migration set.

The current application uses `storage.py` and a local JSON state file. Before public multi-user deployment:

1. Introduce a repository abstraction behind `storage.py`.
2. Use SQLite for single-instance installations and PostgreSQL for hosted deployments.
3. Add migrations for users, refresh tokens, profiles, puzzle attempts, solves, and achievements.
4. Make `DATABASE_URL` select the backend and run migrations as a release step, not during web requests.
5. Keep an export/import path from `~/.lux/state.json` for existing CLI users.

Do not treat the Compose PostgreSQL service as active application persistence until these migrations and repository changes land.
