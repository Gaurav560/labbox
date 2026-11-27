"""Monitoring: daily numbers from Claimdesk's request log, and alerts when they drift. Run it with: python monitor.py"""
import json
import math
from collections import defaultdict

USD_PER_MILLION_IN = 0.15  # gpt-4o-mini (chapter 8)
USD_PER_MILLION_OUT = 0.60
RS_PER_USD = 88.0
WATCH = ["p95_ms", "error_pct", "refer_pct", "no_amount_pct"]


def load_log(path="data/requests.jsonl"):
    """One dict per request: day, ms, in, out (tokens), error (None or the error's name), draft, amount_found."""
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def percentile(values, p):
    """Nearest-rank percentile: the smallest value with at least p% of the values at or below it."""
    ordered = sorted(values)
    return ordered[max(1, math.ceil(p / 100 * len(ordered))) - 1]


def daily_metrics(rows):
    """One dict per day, in date order: {"day", "n", "p50_ms", "p95_ms", "error_pct", "refer_pct", "no_amount_pct",
    "cost_rs"}. Percentages are of all the day's requests, rounded to 1 place; cost_rs is the day's tokens priced like
    chapter 8, rounded to 2 places."""
    by_day = defaultdict(list)
    for row in rows:
        by_day[row["day"]].append(row)
    out = []
    for day in sorted(by_day):
        reqs = by_day[day]
        n = len(reqs)
        ms = [r["ms"] for r in reqs]
        usd = sum(r["in"] * USD_PER_MILLION_IN + r["out"] * USD_PER_MILLION_OUT for r in reqs) / 1_000_000
        out.append({
            "day": day,
            "n": n,
            "p50_ms": percentile(ms, 50),
            "p95_ms": percentile(ms, 95),
            "error_pct": round(sum(1 for r in reqs if r["error"]) / n * 100, 1),
            "refer_pct": round(sum(1 for r in reqs if r["draft"] == "refer") / n * 100, 1),
            "no_amount_pct": round(sum(1 for r in reqs if not r["amount_found"]) / n * 100, 1),
            "cost_rs": round(usd * RS_PER_USD, 2),
        })
    return out


def drift_alerts(days, baseline_days=7, factor=1.5):
    """(day, metric, baseline, value) for every day after the first baseline_days and every metric in WATCH whose value
    is above factor times the baseline. The baseline is the metric's mean over the first baseline_days days, rounded to
    1 place. In day order, then WATCH order."""
    base = {m: round(sum(d[m] for d in days[:baseline_days]) / baseline_days, 1) for m in WATCH}
    alerts = []
    for d in days[baseline_days:]:
        for m in WATCH:
            if d[m] > factor * base[m]:
                alerts.append((d["day"], m, base[m], d[m]))
    return alerts


if __name__ == "__main__":
    days = daily_metrics(load_log())
    print(f"{'day':<11}{'n':>4}{'p50 ms':>8}{'p95 ms':>8}{'err %':>7}{'refer %':>9}{'no amt %':>10}{'cost Rs':>9}")
    for d in days:
        print(f"{d['day']:<11}{d['n']:>4}{d['p50_ms']:>8}{d['p95_ms']:>8}{d['error_pct']:>7}{d['refer_pct']:>9}"
              f"{d['no_amount_pct']:>10}{d['cost_rs']:>9}")
    print("alerts:")
    for day, metric, base, value in drift_alerts(days):
        print(f"   {day} {metric}: {value} (usual {base})")
