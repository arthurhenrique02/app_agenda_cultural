"""Tests for events migration - US-016."""

import os
import subprocess
import sys
from pathlib import Path


def test_events_migration_file_exists() -> None:
    """An Alembic migration for the events table must exist."""
    migration = Path("alembic/versions/d4e5f6a7b8c9_add_events_table.py")
    assert migration.exists(), "Events migration file should exist"


def test_offline_sql_contains_events_table_and_indexes() -> None:
    """Offline SQL generation must include events table and required indexes."""
    env = os.environ.copy()
    env["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost/testdb"

    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head", "--sql"],
        capture_output=True,
        text=True,
        env=env,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0, (
        "alembic upgrade --sql failed:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )

    sql = result.stdout.lower()
    assert "create table events" in sql
    assert "ix_events_status" in sql
    assert "ix_events_date" in sql
    assert "ix_events_category_id" in sql
    assert "ix_events_created_by" in sql
