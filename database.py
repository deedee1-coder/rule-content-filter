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


def row_to_dict(row):
    """Convert a database row into a plain dictionary that Flask can send as JSON."""
    return {
        "id": row["id"],
        "keyword": row["keyword"],
        "match_type": row["match_type"],
        "action_type": row["action_type"],
        "color": row["color"],
        "label": row["label"],
        "enabled": bool(row["enabled"]),
    }


def get_all_rules():
    """Return every rule, oldest first."""
    connection = get_connection()
    rows = connection.execute("SELECT * FROM rules ORDER BY id").fetchall()
    connection.close()
    return [row_to_dict(row) for row in rows]


def create_rule(keyword, match_type, action_type, color, label):
    """Save a new rule and return it (including its new id)."""
    connection = get_connection()
    cursor = connection.execute(
        "INSERT INTO rules (keyword, match_type, action_type, color, label) VALUES (?, ?, ?, ?, ?)",
        (keyword, match_type, action_type, color, label),
    )
    connection.commit()
    row = connection.execute("SELECT * FROM rules WHERE id = ?", (cursor.lastrowid,)).fetchone()
    connection.close()
    return row_to_dict(row)




def get_enabled_rules():
    """Return only enabled rules, oldest first (used when processing text)."""
    connection = get_connection()
    rows = connection.execute("SELECT * FROM rules WHERE enabled = 1 ORDER BY id").fetchall()
    connection.close()
    return [row_to_dict(row) for row in rows]