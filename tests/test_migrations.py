import sqlite3

import pytest

import storage


def write_migration(path, name, sql=""):
    path.mkdir(parents=True, exist_ok=True)
    (path / name).write_text(sql, encoding="utf-8")


def applied_names(db_path):
    with sqlite3.connect(db_path) as conn:
        return [
            row[0]
            for row in conn.execute(
                "SELECT filename FROM schema_migrations ORDER BY filename"
            )
        ]


def test_apply_migrations_creates_tracking_table(tmp_path):
    migrations = tmp_path / "migrations"
    db_path = tmp_path / "lux.db"
    write_migration(migrations, "001_init.sql")

    assert storage.apply_migrations(db_path, migrations) == ["001_init.sql"]
    assert applied_names(db_path) == ["001_init.sql"]


def test_reapplying_migrations_is_noop(tmp_path):
    migrations = tmp_path / "migrations"
    db_path = tmp_path / "lux.db"
    write_migration(migrations, "001_init.sql")

    storage.apply_migrations(db_path, migrations)

    assert storage.apply_migrations(db_path, migrations) == []
    assert storage.pending_migrations(db_path, migrations) == []


def test_new_higher_numbered_migration_is_pending_and_applied(tmp_path):
    migrations = tmp_path / "migrations"
    db_path = tmp_path / "lux.db"
    write_migration(migrations, "001_init.sql")
    storage.apply_migrations(db_path, migrations)

    write_migration(
        migrations,
        "002_add_profiles.sql",
        "CREATE TABLE profiles (id TEXT PRIMARY KEY);",
    )

    assert storage.pending_migrations(db_path, migrations) == ["002_add_profiles.sql"]
    assert storage.apply_migrations(db_path, migrations) == ["002_add_profiles.sql"]
    assert applied_names(db_path) == ["001_init.sql", "002_add_profiles.sql"]


def test_out_of_order_migration_file_raises(tmp_path):
    migrations = tmp_path / "migrations"
    db_path = tmp_path / "lux.db"
    write_migration(migrations, "001_init.sql")
    write_migration(migrations, "003_skips_two.sql")

    with pytest.raises(storage.MigrationError):
        storage.apply_migrations(db_path, migrations)


def test_pending_migrations_dry_run_does_not_apply(tmp_path):
    migrations = tmp_path / "migrations"
    db_path = tmp_path / "lux.db"
    write_migration(migrations, "001_init.sql")

    assert storage.pending_migrations(db_path, migrations) == ["001_init.sql"]
    assert storage.pending_migrations(db_path, migrations) == ["001_init.sql"]
