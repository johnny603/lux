import sqlite3

import pytest

import storage


def test_migrations_fresh_db(tmp_path):
    db_file = tmp_path / "test.db"
    pending = storage.pending_migrations(str(db_file))
    assert "001_init.sql" in pending

    # Dry-run does not apply
    dry = storage.apply_migrations(str(db_file), dry_run=True)
    assert "001_init.sql" in dry
    applied_before = storage.get_applied_migrations(str(db_file))
    assert len(applied_before) == 0

    # Apply migrations
    applied = storage.apply_migrations(str(db_file))
    assert "001_init.sql" in applied

    # Verify tables created
    with sqlite3.connect(str(db_file)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row[0] for row in cursor.fetchall()}
        assert "schema_migrations" in tables
        assert "users" in tables
        assert "profiles" in tables
        assert "puzzle_attempts" in tables
        assert "puzzle_solves" in tables
        assert "achievements" in tables
        assert "refresh_tokens" in tables

    # Re-apply is idempotent
    pending_after = storage.pending_migrations(str(db_file))
    assert len(pending_after) == 0
    applied_again = storage.apply_migrations(str(db_file))
    assert len(applied_again) == 0


def test_migrations_incremental(tmp_path):
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()

    mig1 = migrations_dir / "001_first.sql"
    mig1.write_text("CREATE TABLE t1 (id INTEGER PRIMARY KEY);", encoding="utf-8")

    db_file = tmp_path / "test_incr.db"
    applied = storage.apply_migrations(str(db_file), migrations_dir=str(migrations_dir))
    assert applied == ["001_first.sql"]

    # Add second migration
    mig2 = migrations_dir / "002_second.sql"
    mig2.write_text("CREATE TABLE t2 (id INTEGER PRIMARY KEY, name TEXT);", encoding="utf-8")

    pending = storage.pending_migrations(str(db_file), migrations_dir=str(migrations_dir))
    assert pending == ["002_second.sql"]

    applied2 = storage.apply_migrations(str(db_file), migrations_dir=str(migrations_dir))
    assert applied2 == ["002_second.sql"]

    with sqlite3.connect(str(db_file)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row[0] for row in cursor.fetchall()}
        assert "t1" in tables
        assert "t2" in tables


def test_migrations_out_of_order_raises(tmp_path):
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()

    mig2 = migrations_dir / "002_second.sql"
    mig2.write_text("CREATE TABLE t2 (id INTEGER PRIMARY KEY);", encoding="utf-8")

    db_file = tmp_path / "test_ooo.db"
    # Apply 002 directly
    storage.apply_migrations(str(db_file), migrations_dir=str(migrations_dir))

    # Now introduce 001_first.sql afterwards
    mig1 = migrations_dir / "001_first.sql"
    mig1.write_text("CREATE TABLE t1 (id INTEGER PRIMARY KEY);", encoding="utf-8")

    with pytest.raises(ValueError, match="Out-of-order migration detected"):
        storage.apply_migrations(str(db_file), migrations_dir=str(migrations_dir))


def test_migrations_transaction_rollback_on_error(tmp_path):
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()

    mig1 = migrations_dir / "001_broken.sql"
    mig1.write_text("CREATE TABLE good_table (id INT); SYNTAX ERROR BROKEN SQL;", encoding="utf-8")

    db_file = tmp_path / "test_broken.db"
    with pytest.raises(sqlite3.OperationalError):
        storage.apply_migrations(str(db_file), migrations_dir=str(migrations_dir))

    # Ensure transaction was rolled back and nothing recorded
    with sqlite3.connect(str(db_file)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row[0] for row in cursor.fetchall()}
        assert "good_table" not in tables
        applied = storage.get_applied_migrations(str(db_file))
        assert len(applied) == 0
