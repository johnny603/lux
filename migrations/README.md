# Database migrations

Lux migrations are plain SQLite `.sql` files applied by `storage.apply_migrations`.
The current application still stores player progress in the local JSON state file; the
initial migration records that baseline so later schema changes have a stable starting
point.

## Naming

Use `NNN_short_description.sql`, where `NNN` is a zero-padded, contiguous number:

- `001_init.sql`
- `002_add_profiles.sql`
- `003_add_attempts.sql`

Never renumber migrations after they are merged. A correction to a merged migration is
a new higher-numbered migration, not an edit to the old file.

## Running

The Flask server applies pending migrations on startup. By default the SQLite database
lives at `~/.lux/lux.db`; set `LUX_DB=/path/to/lux.db` to use another file.

To inspect pending migrations without applying them:

```bash
python -m storage --dry-run
```

To apply migrations explicitly:

```bash
python -m storage
```

The runner keeps applied filenames in `schema_migrations(filename, applied_at)` and
applies each pending file in its own transaction. Down-migrations and third-party
migration libraries are intentionally out of scope.
