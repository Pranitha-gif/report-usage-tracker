# report-usage-tracker

A simple BI project that tracks **which reports are used, by whom, and how often**,
and flags stale reports that are candidates for retirement. Pure Python 3.10+ and SQLite, no dependencies.

## Structure
```
report-usage-tracker/
├── main.py                # CLI
├── sample_logs.csv        # example CSV usage log
├── tracker/
│   ├── db.py              # schema (dim_report, dim_user, fact_usage)
│   ├── ingest.py          # record views, load CSV logs
│   ├── sample_data.py     # reproducible demo data
│   ├── analytics.py       # SQL analytics queries
│   └── report.py          # text table + CSV export
└── tests/test_tracker.py
```

## Usage
```bash
python main.py demo                         # sample data + dashboard
python main.py load sample_logs.csv         # ingest a CSV log
python main.py log "Margin Analysis" ravi   # record one view now
python main.py dashboard --export out/ --stale-days 30
python -m pytest tests                      # run tests
```

## Analytics
Top reports, top users, usage by department, daily active users, stale reports.

## Ideas to extend
Streamlit dashboard, Postgres instead of SQLite, scheduled ingestion from a BI tool's audit log, usage-based retirement alerts.
