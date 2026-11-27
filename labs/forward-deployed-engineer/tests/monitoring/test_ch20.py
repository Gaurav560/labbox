import r

ROWS = [
    {"day": "2026-11-02", "ms": 1000, "in": 400, "out": 50, "error": None, "draft": "pay", "amount_found": True},
    {"day": "2026-11-02", "ms": 3000, "in": 0, "out": 0, "error": "APITimeoutError", "draft": "refer", "amount_found": False},
    {"day": "2026-11-01", "ms": 1200, "in": 1_000_000, "out": 0, "error": None, "draft": "refer", "amount_found": True},
    {"day": "2026-11-02", "ms": 2000, "in": 400, "out": 50, "error": None, "draft": "refer", "amount_found": True},
    {"day": "2026-11-02", "ms": 1500, "in": 400, "out": 50, "error": None, "draft": "pay", "amount_found": True},
]


def test_daily_metrics():
    def check():
        from monitor import daily_metrics, load_log
        got = daily_metrics(ROWS)
        if [d.get("day") for d in got] != ["2026-11-01", "2026-11-02"]:
            return r.failed("daily_metrics", "One dict per day, in date order (sort the days).", ["2026-11-01", "2026-11-02"], [d.get("day") for d in got])
        d1, d2 = got
        want = {"day": "2026-11-02", "n": 4, "p50_ms": 1500, "p95_ms": 3000, "error_pct": 25.0, "refer_pct": 50.0,
                "no_amount_pct": 25.0, "cost_rs": 0.02}
        if d2 != want:
            return r.failed("daily_metrics", "Use percentile() for p50 and p95, count errors (error is not None), refer drafts and "
                            "rows without an amount as percents of the day's requests.", want, d2)
        if d1.get("cost_rs") != 13.2:
            return r.failed("daily_metrics", "Price tokens like chapter 8: 1,000,000 input tokens is $0.15, which is Rs 13.20.", 13.2, d1.get("cost_rs"))
        real = daily_metrics(load_log())
        if len(real) != 14 or real[8].get("p95_ms") != 10000:
            return r.failed("daily_metrics", "The real log has 14 days, and on 15 December p95 is 10000 ms.")
        r.passed("daily_metrics", "Fourteen days in one table: speed, errors, refers and cost, the numbers someone will ask about.")
    r.task("daily_metrics", check)


def day(name, **v):
    base = {"day": name, "n": 40, "p50_ms": 1300, "p95_ms": 1800, "error_pct": 2.0, "refer_pct": 30.0, "no_amount_pct": 20.0, "cost_rs": 0.3}
    return {**base, **v}


def test_drift_alerts():
    def check():
        from monitor import daily_metrics, drift_alerts, load_log
        days = [day(f"d{i}") for i in range(7)] + [day("d7", refer_pct=46.0), day("d8", refer_pct=44.0, p95_ms=4000, error_pct=3.0)]
        got = drift_alerts(days)
        want = [("d7", "refer_pct", 30.0, 46.0), ("d8", "p95_ms", 1800.0, 4000)]
        if got != want:
            return r.failed("drift_alerts", "Baseline = the mean of the first 7 days; alert when a later day's value is above 1.5 times it "
                            "(45 for refer_pct, so 44 is fine; 3.0 errors is fine too).", want, got)
        if drift_alerts(days, baseline_days=8) != [("d8", "p95_ms", 1800.0, 4000)]:
            return r.failed("drift_alerts", "Use baseline_days for both the baseline and where checking starts.")
        order = [("d7", "refer_pct", 30.0, 46.0), ("d8", "p95_ms", 1800.0, 4000), ("d8", "error_pct", 2.0, 3.0), ("d8", "refer_pct", 30.0, 44.0)]
        if drift_alerts(days, factor=1.4) != order:
            return r.failed("drift_alerts", "Within a day, follow the order of WATCH: p95_ms, error_pct, refer_pct, no_amount_pct.")
        real = drift_alerts(daily_metrics(load_log()))
        if real[:2] != [("2026-12-15", "p95_ms", 1770.3, 10000), ("2026-12-15", "error_pct", 3.1, 5.3)]:
            return r.failed("drift_alerts", "On the real log, 15 December alerts on p95_ms and error_pct first.", None, real[:2])
        r.passed("drift_alerts", "The slow day and the day the emails changed both stand out, without anyone reading 560 log lines.")
    r.task("drift_alerts", check)
