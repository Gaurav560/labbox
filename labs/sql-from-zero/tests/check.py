"""Live check for sql-from-zero: run each learner query read-only against their database and compare
the rows with a reference query. The learner's files are mounted read-only; their SQL can only read."""
import json
from pathlib import Path

import psycopg

WS = Path("/check/workspace")
TASKS = {
    "q_paid_chai": ("q1.sql", "SELECT id, qty FROM orders WHERE item = 'masala chai' AND status = 'paid' AND outlet_id = 3 ORDER BY id"),
    "q_count_refunds": ("q2.sql", "SELECT COUNT(*) FROM orders WHERE status = 'refunded'"),
    "q_revenue_by_outlet": ("q3.sql", "SELECT o.name, SUM(r.amount_paise) FROM orders r JOIN outlets o ON o.id = r.outlet_id "
                            "WHERE r.status = 'paid' GROUP BY o.name ORDER BY 2 DESC"),
    "q_top_item": ("q4.sql", "SELECT item, SUM(qty) FROM orders WHERE status = 'paid' GROUP BY item ORDER BY 2 DESC LIMIT 1"),
}


def report(task, passed, message, expected=None, actual=None):
    r = {"task": task, "passed": passed, "message": message}
    if expected is not None:
        r["expected"], r["actual"] = expected, actual
    print("@@RESULT " + json.dumps(r, default=str), flush=True)


def run(conn, sql):
    """One statement, read-only, at most 5 seconds; returns (column count, rows)."""
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute("SET LOCAL statement_timeout = '5s'")
            cur.execute(sql)
            if cur.description is None:
                raise ValueError("the query returned no rows (is it a SELECT?)")
            return len(cur.description), [tuple(r) for r in cur.fetchall()]


def short(rows):
    return json.dumps([list(r) for r in rows[:3]], default=str) + (" ..." if len(rows) > 3 else "")


try:
    conn = psycopg.connect(host="db", user="postgres", password="labpass", dbname="tapri", connect_timeout=5, autocommit=True)
except Exception as e:
    for t in TASKS:
        report(t, False, f"Could not connect to the database: {e}")
    raise SystemExit(0)

for task, (file, reference) in TASKS.items():
    path = WS / file
    sql = path.read_text(encoding="utf-8").strip() if path.is_file() else ""
    body = "\n".join(l for l in sql.splitlines() if not l.strip().startswith("--")).strip().rstrip(";").strip()
    if not body:
        report(task, False, f"Write your query in {file}.")
        continue
    if ";" in body:
        report(task, False, f"{file} should hold one query (remove the extra statements).")
        continue
    try:
        want_cols, want = run(conn, reference)
    except Exception as e:
        report(task, False, f"The orders data is missing ({e}). Press Reset lab.")
        continue
    try:
        cols, got = run(conn, body)
    except Exception as e:
        report(task, False, f"{file} failed: {str(e).splitlines()[0]}")
        continue
    if cols != want_cols:
        report(task, False, f"{file} returns {cols} column(s); the answer has {want_cols}.", f"{want_cols} columns", f"{cols} columns")
    elif len(got) != len(want):
        report(task, False, f"{file} returns {len(got)} row(s); the answer has {len(want)}.", f"{len(want)} rows", f"{len(got)} rows")
    elif got != want:
        first = next(i for i, (a, b) in enumerate(zip(got, want)) if a != b)
        report(task, False, f"Row {first + 1} of {file} is different (check the filter and the order).", short(want[first:]), short(got[first:]))
    else:
        report(task, True, f"{len(got)} row(s), all correct.")
