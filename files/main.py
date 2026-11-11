"""CLI for report-usage-tracker.

Examples:
    python main.py demo                      # create DB, load sample data, print dashboard
    python main.py load logs.csv             # ingest a CSV usage log
    python main.py log "Margin Analysis" ravi  # record one view right now
    python main.py dashboard --export out/   # print dashboard and export CSVs
"""
import argparse
from datetime import datetime

from tracker import analytics, db, ingest, report, sample_data


def dashboard(conn, export_dir=None, stale_days=30):
    sections = {
        "top_reports": ("Top reports", analytics.top_reports(conn)),
        "top_users": ("Top users", analytics.top_users(conn)),
        "usage_by_department": ("Usage by department", analytics.usage_by_department(conn)),
        "daily_active_users": ("Daily active users (last 14 days)", analytics.daily_active_users(conn)),
        "stale_reports": (f"Stale reports (no views in {stale_days} days)",
                          analytics.stale_reports(conn, stale_days)),
    }
    for key, (title, rows) in sections.items():
        print(report.format_table(rows, title))
        if export_dir:
            report.export_csv(rows, f"{export_dir}/{key}.csv")


def main():
    p = argparse.ArgumentParser(description="BI report usage tracker")
    p.add_argument("--db", default="data/usage.db")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("demo", help="load sample data and show dashboard")
    sp = sub.add_parser("load", help="ingest a CSV log")
    sp.add_argument("csv_path")
    sp = sub.add_parser("log", help="record a single view now")
    sp.add_argument("report_name")
    sp.add_argument("user_name")
    sp.add_argument("--duration", type=int, default=0)
    sp = sub.add_parser("dashboard", help="print analytics")
    sp.add_argument("--export", help="directory for CSV exports")
    sp.add_argument("--stale-days", type=int, default=30)

    args = p.parse_args()
    conn = db.connect(args.db)
    db.init_db(conn)

    if args.cmd == "demo":
        sample_data.populate(conn)
        dashboard(conn)
    elif args.cmd == "load":
        print(f"Loaded {ingest.load_csv(conn, args.csv_path)} events")
    elif args.cmd == "log":
        ingest.record_view(conn, args.report_name, args.user_name,
                           datetime.now().isoformat(timespec="seconds"), args.duration)
        conn.commit()
        print("Recorded.")
    elif args.cmd == "dashboard":
        dashboard(conn, args.export, args.stale_days)


if __name__ == "__main__":
    main()
