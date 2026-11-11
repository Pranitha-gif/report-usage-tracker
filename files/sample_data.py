"""Generate reproducible sample reports, users and usage events."""
import random
from datetime import datetime, timedelta

REPORTS = [
    ("Daily Sales Summary", "Sales"), ("Margin Analysis", "Finance"),
    ("Customer Churn", "Marketing"), ("Inventory Levels", "Operations"),
    ("Headcount Overview", "HR"), ("Collateral Exposure", "Risk"),
    ("Legacy Revenue Report", "Finance"), ("Regional KPI Pack", "Sales"),
]
USERS = [
    ("asha", "Sales"), ("ravi", "Finance"), ("meena", "Marketing"),
    ("kiran", "Operations"), ("sita", "HR"), ("arjun", "Risk"),
    ("divya", "Finance"), ("rahul", "Sales"),
]


def populate(conn, days: int = 60, events: int = 600, seed: int = 42,
             today: datetime | None = None) -> None:
    rng = random.Random(seed)
    today = today or datetime.now().replace(microsecond=0)

    for i, (name, team) in enumerate(REPORTS, start=1):
        created = (today - timedelta(days=200 + i * 5)).date().isoformat()
        conn.execute(
            "INSERT OR IGNORE INTO dim_report(report_name, owner_team, created_on) VALUES (?,?,?)",
            (name, team, created),
        )
    for name, dept in USERS:
        conn.execute("INSERT OR IGNORE INTO dim_user(user_name, department) VALUES (?,?)", (name, dept))

    report_ids = [r["report_id"] for r in conn.execute("SELECT report_id FROM dim_report ORDER BY report_id")]
    names = {r["report_id"]: r["report_name"] for r in conn.execute("SELECT * FROM dim_report")}
    user_ids = [r["user_id"] for r in conn.execute("SELECT user_id FROM dim_user")]
    # popularity weights: early reports popular, "Legacy" report nearly unused
    weights = [10, 8, 6, 5, 3, 4, 0.2, 7][: len(report_ids)]

    for _ in range(events):
        rid = rng.choices(report_ids, weights=weights)[0]
        offset = rng.randint(0, days * 24 * 60)
        if names[rid] == "Legacy Revenue Report":  # only viewed long ago -> stale
            offset = rng.randint(45 * 24 * 60, days * 24 * 60)
        ts = (today - timedelta(minutes=offset)).replace(microsecond=0).isoformat(timespec="seconds")
        conn.execute(
            "INSERT INTO fact_usage(report_id, user_id, viewed_at, duration_secs) VALUES (?,?,?,?)",
            (rid, rng.choice(user_ids), ts, rng.randint(10, 900)),
        )
    conn.commit()
