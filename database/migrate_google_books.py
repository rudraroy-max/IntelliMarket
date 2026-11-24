"""Back up prices.db, then apply the additive Google Books catalog schema."""

import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

from database.connection import DATABASE_PATH


MIGRATION_PATH = Path(__file__).resolve().parent / "migrations" / "001_google_books_catalog.sql"


def migrate(database_path=DATABASE_PATH):
    database_path = Path(database_path).resolve()
    if not database_path.exists():
        raise FileNotFoundError(f"Database does not exist: {database_path}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_path = database_path.with_name(
        f"{database_path.stem}.before_google_books_{timestamp}{database_path.suffix}"
    )
    migration_sql = MIGRATION_PATH.read_text(encoding="utf-8")
    with closing(sqlite3.connect(database_path)) as connection:
        with closing(sqlite3.connect(backup_path)) as backup:
            connection.backup(backup)
            if backup.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise RuntimeError("Database backup verification failed.")

        connection.execute("PRAGMA foreign_keys = ON")
        with connection:
            connection.executescript("BEGIN IMMEDIATE;\n" + migration_sql + "\nCOMMIT;")

    return backup_path


if __name__ == "__main__":
    print(f"Migration complete. Backup: {migrate()}")
