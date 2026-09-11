import sqlite3

from config import DATABASE_PATH


def get_connection():
    """Open a connection to the SQLite database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row  # lets us read columns by name: row["keyword"]
    return connection


def init_db():
    """Create the rules table if it does not exist yet."""
    connection = get_connection()
    connection.execute("""
        CREATE TABLE IF NOT EXISTS rules (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword     TEXT    NOT NULL,
            match_type  TEXT    NOT NULL,
            action_type TEXT    NOT NULL,
            color       TEXT,
            label       TEXT,
            enabled     INTEGER NOT NULL DEFAULT 1
        )
    """)
    connection.commit()
    connection.close()