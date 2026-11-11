"""Analytics queries over the usage tables. Each returns a list of dict rows."""
from datetime import datetime, timedelta


def _rows(cur):
    return [dict(r) for r in cur.fetchall()]


def top_reports(conn, limit=5):
    return _rows(conn.execute("""
        SELECT r.report_name,
               COUNT(*)                         AS views,
               COUNT(DISTINCT f.user_id)        AS unique_users,
               ROUND(AVG(f.duration_secs), 1)   AS avg_duration_secs
        FROM fact_usage f JOIN dim_report r USING (report_id)
        GROUP BY r.report_id
        ORDER BY views DESC
        LIMIT ?""", (limit,)))


def daily_active_users(conn, days=14, today=None):
    today = today or datetime.now()
    since = (today - timedelta(days=days)).date().isoformat()
    return _rows(conn.execute("""
        SELECT substr(viewed_at, 1, 10) AS day,
               COUNT(DISTINCT user_id)  AS active_users,
               COUNT(*)                 AS views
        FROM fact_usage
        WHERE substr(viewed_at, 1, 10) >= ?
        GROUP BY day ORDER BY day""", (since,)))


def usage_by_department(conn):
    return _rows(conn.execute("""
        SELECT u.department, COUNT(*) AS views,
               COUNT(DISTINCT f.report_id) AS reports_used
        FROM fact_usage f JOIN dim_user u USING (user_id)
        GROUP BY u.department ORDER BY views DESC"""))


def stale_reports(conn, stale_days=30, today=None):
    """Reports with no views in the last `stale_days` (candidates to retire)."""
    today = today or datetime.now()
    cutoff = (today - timedelta(days=stale_days)).isoformat(timespec="seconds")
    return _rows(conn.execute("""
        SELECT r.report_name, r.owner_team,
               MAX(f.viewed_at) AS last_viewed,
               COUNT(f.event_id) AS lifetime_views
        FROM dim_report r LEFT JOIN fact_usage f USING (report_id)
        GROUP BY r.report_id
        HAVING last_viewed IS NULL OR last_viewed < ?
        ORDER BY last_viewed""", (cutoff,)))


def top_users(conn, limit=5):
    return _rows(conn.execute("""
        SELECT u.user_name, u.department, COUNT(*) AS views,
               COUNT(DISTINCT f.report_id) AS reports_used
        FROM fact_usage f JOIN dim_user u USING (user_id)
        GROUP BY u.user_id ORDER BY views DESC LIMIT ?""", (limit,)))
