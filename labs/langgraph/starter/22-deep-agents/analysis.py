"""Exact numbers from the complaints file, for the data-analyst subagent (models should not count rows by eye)."""
import csv
from collections import Counter
from pathlib import Path

from langchain.tools import tool

DATA = Path(__file__).parent / "data" / "complaints_2025.csv"


@tool
def count_complaints(street: str = "", kind: str = "", months: str = "") -> str:
    """Count complaints in complaints_2025.csv. Every filter is optional: street (e.g. "Station Road"), kind
    (leak, no_water, dirty_water, billing), months (comma-separated, e.g. "2025-06,2025-07"). Returns counts per
    street and kind, largest first, and the total."""
    wanted = {m.strip() for m in months.split(",") if m.strip()}
    with DATA.open() as f:
        rows = [r for r in csv.DictReader(f)
                if (not street or r["street"] == street) and (not kind or r["kind"] == kind)
                and (not wanted or r["month"] in wanted)]
    counts = Counter((r["street"], r["kind"]) for r in rows)
    lines = [f"{s}, {k}: {n}" for (s, k), n in counts.most_common()]
    return "\n".join(lines + [f"total: {len(rows)}"])
