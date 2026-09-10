# Database migrations

This directory contains database schema migrations for Lux.

## Naming convention

Migration files must follow the strict naming pattern:
`NNN_short_description.sql`

- `NNN`: 3-digit zero-padded integer (e.g. `001_init.sql`, `002_add_room_states.sql`).
- Never renumber or rename existing migrations.
- Merged migrations are **immutable**. Any fixes or schema changes must be added as a new, higher-numbered migration file.

## Schema tracking

Applied migrations are tracked in the `schema_migrations` table:
```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
    filename TEXT PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Running migrations

Migrations are applied automatically at application startup via `storage.apply_migrations(db_path)` before serving traffic.

You can also use the migration runner programmatically:
- `storage.pending_migrations(db_path)`: Returns a list of pending migration filenames.
- `storage.apply_migrations(db_path, dry_run=True)`: Prints/returns pending migrations without applying changes.
- `storage.apply_migrations(db_path)`: Executes each pending migration inside its own transaction and records it in `schema_migrations`.

## Scope and architecture

- Lightweight and dependency-free (using standard library `sqlite3`).
- Single transaction per migration file — if a migration fails, changes are rolled back.
- Out-of-order execution or missing files raise descriptive errors.

The current application uses `storage.py` and a local JSON state file alongside SQLite migrations. Before public multi-user deployment:

1. Introduce a repository abstraction behind `storage.py`.
2. Use SQLite for single-instance installations and PostgreSQL for hosted deployments.
3. Add migrations for users, refresh tokens, profiles, puzzle attempts, solves, and achievements.
4. Make `DATABASE_URL` select the backend and run migrations as a release step, not during web requests.
5. Keep an export/import path from `~/.lux/state.json` for existing CLI users.

Do not treat the Compose PostgreSQL service as active application persistence until these migrations and repository changes land.

