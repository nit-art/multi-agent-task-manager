"""
database/db.py
--------------
SQLite storage for tasks and notes.
• init_db()       — called once at startup to create tables
• get_connection() — used by every tool to read/write data
"""

import sqlite3
import os

# DB file lives inside the /database folder so it's easy to locate or reset
DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")


def get_connection() -> sqlite3.Connection:
    """Return an open SQLite connection. Rows behave like dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # row["title"] instead of row[1]
    return conn


def init_db() -> None:
    """
    Create the 'tasks' and 'notes' tables if they don't exist yet.
    Called once from main.py on application startup.
    """
    conn = get_connection()
    cur  = conn.cursor()

    # ---------- tasks ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id         INTEGER  PRIMARY KEY AUTOINCREMENT,
            title      TEXT     NOT NULL,
            status     TEXT     NOT NULL DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ---------- notes ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id         INTEGER  PRIMARY KEY AUTOINCREMENT,
            content    TEXT     NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()