"""Tests for US-004: Alembic async migrations setup."""

import os
import subprocess
import sys
from pathlib import Path


def test_alembic_ini_exists():
    """alembic.ini config file is present in the project root."""
    assert Path("alembic.ini").exists(), "alembic.ini should exist at project root"


def test_alembic_versions_dir_exists():
    """The alembic/versions directory exists and is a directory."""
    versions = Path("alembic/versions")
    assert versions.exists() and versions.is_dir()


def test_at_least_one_migration_file_exists():
    """At least one migration file is generated (baseline)."""
    versions = Path("alembic/versions")
    migration_files = [f for f in versions.glob("*.py") if not f.name.startswith("__")]
    assert len(migration_files) >= 1, "Baseline migration file should exist"


def test_baseline_migration_has_revision():
    """The baseline migration file defines a revision ID and no parent."""
    versions = Path("alembic/versions")
    migration_files = [f for f in versions.glob("*.py") if not f.name.startswith("__")]
    content = migration_files[0].read_text()
    assert "revision:" in content
    assert "down_revision" in content


def test_offline_sql_generation():
    """Alembic can generate SQL in offline mode without a live DB connection."""
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
    assert "alembic_version" in result.stdout


def test_base_metadata_is_importable():
    """app.models.Base is importable and has metadata."""
    from app.models.base import Base

    assert Base.metadata is not None


def test_env_py_imports_base():
    """alembic/env.py references app.models for autogenerate."""
    env_py = Path("alembic/env.py").read_text()
    assert "app.models" in env_py, "env.py should import app.models for autogenerate"
    assert "target_metadata" in env_py
