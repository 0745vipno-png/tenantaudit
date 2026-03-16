"""
TenantAudit Database Layer
==========================

Provides SQLite database initialization and connection management.

Design Goals
------------
- Single database entry point
- Enforce foreign key integrity
- Enable WAL mode for reliability
- Initialize schema automatically
- Safe connection lifecycle

Usage
-----
from tenantaudit.storage.db import get_connection, initialize_database
"""

from pathlib import Path
import sqlite3


DEFAULT_DB_PATH = "tenantaudit.db"
SCHEMA_FILE = "schema.sql"


# ---------------------------------------------------------
# Connection
# ---------------------------------------------------------

def get_connection(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """
    Create a SQLite connection with required safety settings.
    """

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")

    # Use WAL for better concurrency
    conn.execute("PRAGMA journal_mode = WAL;")

    # Reasonable durability
    conn.execute("PRAGMA synchronous = NORMAL;")

    return conn


# ---------------------------------------------------------
# Schema Initialization
# ---------------------------------------------------------

def initialize_database(
    db_path: str | Path = DEFAULT_DB_PATH,
    schema_path: str | Path = SCHEMA_FILE,
) -> None:
    """
    Initialize database using schema.sql.

    Safe to run multiple times.
    """

    schema_path = Path(schema_path)

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    conn = get_connection(db_path)

    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        conn.executescript(schema_sql)
        conn.commit()

    finally:
        conn.close()


# ---------------------------------------------------------
# Utility
# ---------------------------------------------------------

def database_exists(db_path: str | Path = DEFAULT_DB_PATH) -> bool:
    """
    Check whether the database file exists.
    """
    return Path(db_path).exists()


def ensure_database(
    db_path: str | Path = DEFAULT_DB_PATH,
    schema_path: str | Path = SCHEMA_FILE,
) -> None:
    """
    Ensure the database exists and is initialized.
    """

    if not database_exists(db_path):
        initialize_database(db_path, schema_path)