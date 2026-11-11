"""SQLite schema and connection helpers."""
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS dim_report (
    report_id   INTEGER PRIMARY KEY,
    report_name TEXT NOT NULL UNIQUE,
    owner_team  TEXT NOT NULL,
    created_on  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_user (
    user_id    INTEGER PRIMARY KEY,
    user_name  TEXT NOT NULL UNIQUE,
    department TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_usage (
    event_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id     INTEGER NOT NULL REFERENCES dim_report(report_id),
    user_id       INTEGER NOT NULL REFERENCES dim_user(user_id),
    viewed_at     TEXT NOT NULL,          -- ISO timestamp
    duration_secs INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_usage_report ON fact_usage(report_id);
CREATE INDEX IF NOT EXISTS idx_usage_user   ON fact_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_date   ON fact_usage(viewed_at);
"""


def connect(db_path: str = "data/usage.db") -> sqlite3.Connection:
    if db_path != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()
