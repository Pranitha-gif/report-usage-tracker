"""Record usage events and load them from CSV logs."""
import csv
import sqlite3


def _get_or_create_report(conn, name, owner_team="unknown", created_on="1970-01-01"):
    row = conn.execute("SELECT report_id FROM dim_report WHERE report_name=?", (name,)).fetchone()
    if row:
        return row["report_id"]
    cur = conn.execute(
        "INSERT INTO dim_report(report_name, owner_team, created_on) VALUES (?,?,?)",
        (name, owner_team, created_on),
    )
    return cur.lastrowid


def _get_or_create_user(conn, name, department="unknown"):
    row = conn.execute("SELECT user_id FROM dim_user WHERE user_name=?", (name,)).fetchone()
    if row:
        return row["user_id"]
    cur = conn.execute(
        "INSERT INTO dim_user(user_name, department) VALUES (?,?)", (name, department)
    )
    return cur.lastrowid


def record_view(conn: sqlite3.Connection, report_name: str, user_name: str,
                viewed_at: str, duration_secs: int = 0) -> None:
    """Log one report view. Unknown reports/users are created automatically."""
    rid = _get_or_create_report(conn, report_name)
    uid = _get_or_create_user(conn, user_name)
    conn.execute(
        "INSERT INTO fact_usage(report_id, user_id, viewed_at, duration_secs) VALUES (?,?,?,?)",
        (rid, uid, viewed_at, int(duration_secs)),
    )


def load_csv(conn: sqlite3.Connection, path: str) -> int:
    """Load a CSV with columns: report_name,user_name,viewed_at,duration_secs."""
    count = 0
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            record_view(conn, row["report_name"], row["user_name"],
                        row["viewed_at"], row.get("duration_secs") or 0)
            count += 1
    conn.commit()
    return count
