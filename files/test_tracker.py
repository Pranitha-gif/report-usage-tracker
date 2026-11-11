import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from datetime import datetime, timedelta
from tracker import analytics, db, ingest


def make_conn():
    conn = db.connect(":memory:")
    db.init_db(conn)
    return conn


def test_record_and_top_reports():
    conn = make_conn()
    now = datetime(2026, 11, 10, 12, 0, 0)
    for _ in range(3):
        ingest.record_view(conn, "A", "u1", now.isoformat(), 60)
    ingest.record_view(conn, "B", "u2", now.isoformat(), 30)
    top = analytics.top_reports(conn)
    assert top[0]["report_name"] == "A"
    assert top[0]["views"] == 3 and top[0]["unique_users"] == 1


def test_stale_reports():
    conn = make_conn()
    now = datetime(2026, 11, 10)
    ingest.record_view(conn, "Fresh", "u1", (now - timedelta(days=2)).isoformat())
    ingest.record_view(conn, "Old", "u1", (now - timedelta(days=90)).isoformat())
    stale = [r["report_name"] for r in analytics.stale_reports(conn, 30, today=now)]
    assert stale == ["Old"]


def test_daily_active_users():
    conn = make_conn()
    now = datetime(2026, 11, 10)
    ingest.record_view(conn, "A", "u1", now.isoformat())
    ingest.record_view(conn, "A", "u2", now.isoformat())
    dau = analytics.daily_active_users(conn, 7, today=now)
    assert dau[-1]["active_users"] == 2
