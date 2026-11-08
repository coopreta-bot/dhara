"""Apply ordered RAG vector-store SQL migrations to self-hosted Postgres."""

from __future__ import annotations

import argparse
import asyncio
from collections.abc import Iterable
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from rag.database import _get_database_url

MIGRATIONS_DIR = Path(__file__).with_name("migrations")
MIGRATION_TABLE = "dhara_schema_migrations"

CREATE_MIGRATION_TABLE = f"""
CREATE TABLE IF NOT EXISTS {MIGRATION_TABLE} (
  name TEXT PRIMARY KEY,
  applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""


def migration_files(migrations_dir: Path = MIGRATIONS_DIR) -> list[Path]:
    """Return numbered SQL migrations in deterministic order."""
    return sorted(
        path for path in migrations_dir.glob("[0-9][0-9][0-9][0-9]_*.sql") if path.is_file()
    )


def sql_statements(sql: str) -> Iterable[str]:
    """Split the repository's simple migration files into executable statements."""
    without_comment_lines = "\n".join(
        line for line in sql.splitlines() if not line.lstrip().startswith("--")
    )
    return (
        statement.strip() for statement in without_comment_lines.split(";") if statement.strip()
    )


async def apply_migrations() -> list[str]:
    """Apply every unapplied local migration and return their filenames."""
    engine = create_async_engine(_get_database_url(), pool_pre_ping=True)
    applied: list[str] = []

    try:
        async with engine.begin() as connection:
            await connection.execute(text(CREATE_MIGRATION_TABLE))

        for migration_path in migration_files():
            migration_name = migration_path.name
            async with engine.begin() as connection:
                already_applied = await connection.execute(
                    text(f"SELECT 1 FROM {MIGRATION_TABLE} WHERE name = :name"),
                    {"name": migration_name},
                )
                if already_applied.scalar_one_or_none() is not None:
                    continue

                for statement in sql_statements(migration_path.read_text(encoding="utf-8")):
                    await connection.execute(text(statement))
                await connection.execute(
                    text(f"INSERT INTO {MIGRATION_TABLE} (name) VALUES (:name)"),
                    {"name": migration_name},
                )
                applied.append(migration_name)
    finally:
        await engine.dispose()

    return applied


def main() -> None:
    """Apply migrations with the database selected by DHARA_DATABASE_URL."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    applied = asyncio.run(apply_migrations())
    if applied:
        print(f"Applied migrations: {', '.join(applied)}")
    else:
        print("No pending migrations.")


if __name__ == "__main__":
    main()
