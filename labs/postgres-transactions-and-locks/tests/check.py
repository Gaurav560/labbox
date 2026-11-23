"""Live checks for postgres-transactions-and-locks. The checker tries the learner's database inside
transactions it always rolls back, so a Check never changes their data."""
import json
import re

import psycopg
from psycopg import errors

TASKS = ("no_negative", "atomic_transfer", "kill_blocker", "idle_timeout")


def report(task, passed, message, expected=None, actual=None):
    r = {"task": task, "passed": passed, "message": message}
    if expected is not None:
        r["expected"], r["actual"] = expected, actual
    print("@@RESULT " + json.dumps(r), flush=True)


class Rollback(Exception):
    pass


def trial(conn, fn):
    """Run fn(cursor) in a transaction that is always rolled back; returns what fn returns."""
    out = None
    try:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute("SET LOCAL lock_timeout = '2s'")
                cur.execute("SET LOCAL statement_timeout = '5s'")
                out = fn(cur)
            raise Rollback
    except Rollback:
        pass
    return out


def table_exists(cur, name):
    cur.execute("SELECT to_regclass(%s)", (f"public.{name}",))
    return cur.fetchone()[0] is not None


# ---------- chapter 1 ----------

def no_negative(conn):
    with conn.cursor() as cur:
        if not table_exists(cur, "wallets"):
            return report("no_negative", False, "The wallets table is missing. Open chapter 1 again, or press Reset lab.")
        cur.execute("SELECT count(*), count(*) FILTER (WHERE balance_paise < 0) FROM wallets")
        total, negative = cur.fetchone()
    if total < 8:
        return report("no_negative", False, "Wallets were deleted. Fix the balance instead (Reset lab brings them back).", "8 wallets", f"{total}")
    if negative:
        return report("no_negative", False, f"{negative} wallet(s) are still below zero. Fix the data first.", "0", str(negative))

    def try_negative(cur):
        try:
            with conn.transaction():
                cur.execute("UPDATE wallets SET balance_paise = -1 WHERE customer_id = 1")
            return "allowed"
        except errors.CheckViolation:
            return "blocked"
    if trial(conn, try_negative) != "blocked":
        return report("no_negative", False, "The database still accepts a negative balance. Add a CHECK constraint.",
                      "a check_violation error", "the update went through")
    report("no_negative", True, "No wallet can go below zero, whatever the app does.")


def atomic_transfer(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regprocedure('transfer(integer,integer,integer)')")
        if cur.fetchone()[0] is None:
            return report("atomic_transfer", False, "There is no transfer(integer, integer, integer) function yet. Load it with psql -f transfer.sql.")

    def snapshot(cur):
        cur.execute("SELECT customer_id, balance_paise FROM wallets ORDER BY customer_id")
        balances = dict(cur.fetchall())
        cur.execute("SELECT count(*) FROM ledger")
        return balances, cur.fetchone()[0]

    def call(cur, a, b, amount):
        """(error name or None, balances before, after, ledger rows before, after, new ledger row)"""
        before, rows_before = snapshot(cur)
        error = None
        try:
            with conn.transaction():
                cur.execute("SELECT transfer(%s, %s, %s)", (a, b, amount))
        except psycopg.Error as e:
            error = type(e).__name__
        after, rows_after = snapshot(cur)
        cur.execute("SELECT from_customer, to_customer, amount_paise FROM ledger ORDER BY id DESC LIMIT 1")
        return error, before, after, rows_before, rows_after, cur.fetchone()

    def good(cur):
        err, b, a, rb, ra, last = call(cur, 3, 2, 1500)
        if err:
            return f"transfer(3, 2, 1500) failed with {err}, but Meera has enough money."
        if a.get(3) != b[3] - 1500 or a.get(2) != b[2] + 1500:
            return f"After transfer(3, 2, 1500) the balances are {a.get(3)} and {a.get(2)}; expected {b[3] - 1500} and {b[2] + 1500}."
        if ra != rb + 1 or tuple(last) != (3, 2, 1500):
            return "transfer(3, 2, 1500) did not add one ledger row (3, 2, 1500)."
        return None

    def all_or_nothing(cur):
        for args, why in (((4, 1, 90000), "Kabir only has 800 paise"), ((1, 424242, 500), "customer 424242 has no wallet")):
            err, b, a, rb, ra, _ = call(cur, *args)
            if not err:
                return f"transfer{args} succeeded, but {why}. It must fail with an error."
            if a != b or ra != rb:
                return f"transfer{args} failed, but some changes stayed. All or nothing."
        return None

    problem = trial(conn, good) or trial(conn, all_or_nothing)
    if problem:
        return report("atomic_transfer", False, problem)
    report("atomic_transfer", True, "Good transfers move money and log it; bad ones change nothing.")


# ---------- chapter 2 ----------

def kill_blocker(conn):
    with conn.cursor() as cur:
        if not table_exists(cur, "orders"):
            return report("kill_blocker", False, "The orders table is missing. Open chapter 2 again, or press Reset lab.")
        cur.execute("SELECT count(*) FROM orders WHERE id = 42")
        if cur.fetchone()[0] != 1:
            return report("kill_blocker", False, "Order 42 is gone. The customer still needs it (Reset lab brings it back).")

    def pay(cur):
        try:
            with conn.transaction():
                cur.execute("UPDATE orders SET status = 'paid' WHERE id = 42")
            return None
        except errors.LockNotAvailable:
            return "waiting"
    if trial(conn, pay) == "waiting":
        return report("kill_blocker", False, "Paying order 42 still waits on a lock. Something is holding it.",
                      "the update finishes", "still waiting after 2 s")
    report("kill_blocker", True, "Checkout goes through again.")


def idle_timeout(conn):
    with conn.cursor() as cur:
        cur.execute("""SELECT unnest(s.setconfig) FROM pg_db_role_setting s JOIN pg_database d ON d.oid = s.setdatabase
                       WHERE d.datname = current_database() AND s.setrole = 0""")
        settings = [r[0] for r in cur.fetchall()]
    value = next((s.split("=", 1)[1] for s in settings if s.startswith("idle_in_transaction_session_timeout=")), None)
    if value is None:
        return report("idle_timeout", False, "The shop database has no idle_in_transaction_session_timeout yet.", "a timeout on the database", "none")
    m = re.fullmatch(r"(\d+)\s*(ms|s|min)?", value.strip())
    if not m:
        return report("idle_timeout", False, f"Could not read the timeout {value!r}.")
    ms = int(m.group(1)) * {"ms": 1, None: 1, "s": 1000, "min": 60000}[m.group(2)]
    if ms == 0:
        return report("idle_timeout", False, "A timeout of 0 means no timeout at all.", "1 s to 5 min", value)
    if ms > 300_000:
        return report("idle_timeout", False, "That is too long: a forgotten transaction would still block checkout for minutes.", "5 min or less", value)
    report("idle_timeout", True, f"Forgotten transactions now end on their own after {value}.")


try:
    conn = psycopg.connect(host="db", user="postgres", password="labpass", dbname="shop", connect_timeout=5, autocommit=True)
except Exception as e:
    for t in TASKS:
        report(t, False, f"Could not connect to the database: {e}")
    raise SystemExit(0)

for check in (no_negative, atomic_transfer, kill_blocker, idle_timeout):
    try:
        check(conn)
    except Exception as e:
        report(check.__name__, False, f"The check could not finish: {str(e).splitlines()[0]}")
