"""Plain-text and CSV output helpers."""
import csv
from pathlib import Path


def format_table(rows, title=""):
    if not rows:
        return f"\n{title}\n(no data)\n"
    cols = list(rows[0].keys())
    widths = {c: max(len(c), *(len(str(r[c])) for r in rows)) for c in cols}
    line = "  ".join(c.ljust(widths[c]) for c in cols)
    sep = "  ".join("-" * widths[c] for c in cols)
    body = "\n".join("  ".join(str(r[c]).ljust(widths[c]) for c in cols) for r in rows)
    return f"\n== {title} ==\n{line}\n{sep}\n{body}\n"


def export_csv(rows, path):
    if not rows:
        return
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
