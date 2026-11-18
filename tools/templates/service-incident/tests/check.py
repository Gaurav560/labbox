"""Live check for the slow checkout: the lookup must use an index and run in under 5 ms."""
import json

import psycopg

TARGET_MS = 5.0
CUSTOMERS = (4242, 17, 31337)
QUERY = "SELECT id, item, amount_paise, created_at FROM orders WHERE customer_id = %s ORDER BY created_at DESC LIMIT 20"


def report(task, passed, message, expected=None, actual=None):
    r = {"task": task, "passed": passed, "message": message}
    if expected is not None:
        r["expected"], r["actual"] = expected, actual
    print("@@RESULT " + json.dumps(r), flush=True)


def metric(name, value, target, better):
    print("@@METRIC " + json.dumps({"name": name, "value": value, "target": target, "better": better}), flush=True)


def nodes(plan):
    yield plan
    for child in plan.get("Plans", []):
        yield from nodes(child)


try:
    conn = psycopg.connect(host="db", user="postgres", password="labpass", dbname="tapri", connect_timeout=5)
except Exception as e:
    report("add_index", False, f"Could not connect to the database: {e}")
    raise SystemExit(0)

with conn, conn.cursor() as cur:
    cur.execute("SELECT to_regclass('public.orders')")
    if cur.fetchone()[0] is None:
        report("add_index", False, "The orders table is missing. Press Reset lab to get it back.")
        raise SystemExit(0)
    cur.execute("SELECT count(*) FROM orders")
    rows = cur.fetchone()[0]
    if rows < 990_000:
        # Deleting orders would make anything fast. The shop needs its history.
        report("add_index", False, f"Only {rows} orders are left. Fix the speed without deleting data (Reset lab restores it).",
               ">= 1000000 orders", f"{rows} orders")
        raise SystemExit(0)

    worst_ms, seq_scan = 0.0, False
    for customer in CUSTOMERS:
        for _ in range(2):  # the first run warms the cache; keep the second
            cur.execute("EXPLAIN (ANALYZE, FORMAT JSON) " + QUERY, (customer,))
            plan = cur.fetchone()[0][0]
        ms = plan["Execution Time"]
        worst_ms = max(worst_ms, ms)
        seq_scan |= any(n["Node Type"] == "Seq Scan" and n.get("Relation Name") == "orders" for n in nodes(plan["Plan"]))

    metric("lookup_ms", round(worst_ms, 2), TARGET_MS, "lower")
    if seq_scan:
        report("add_index", False, "Postgres still reads the whole orders table (Seq Scan) for one customer.",
               "an index scan", f"Seq Scan, {worst_ms:.1f} ms")
    elif worst_ms > TARGET_MS:
        report("add_index", False, f"It uses an index now, but the lookup takes {worst_ms:.1f} ms.",
               f"< {TARGET_MS:g} ms", f"{worst_ms:.1f} ms")
    else:
        report("add_index", True, f"Lookup takes {worst_ms:.2f} ms with an index. Lunch rush is saved.")
