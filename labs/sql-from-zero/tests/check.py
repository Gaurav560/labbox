"""Live check for sql-from-zero (Safar, a bus ticket booking app).

Query tasks: run the learner's query from its file, read-only and at most 5 seconds, and compare the rows with a
reference query. Tasks that change data (chapters 9 to 11) are checked by reading the database's state. Only the
tasks in LABBOX_TASKS run (all of them when it is not set). The learner's files are mounted read-only.
"""
import json
import os
from decimal import Decimal
from pathlib import Path

import psycopg

WS = Path("/check/workspace")
WANTED = {t for t in os.environ.get("LABBOX_TASKS", "").split(",") if t}

# task: (file, reference query, the order matters, column names the task asks for or None)
QUERIES = {
    # chapter 1: why databases exist
    "count_cities": ("01-why-databases/q1.sql", "SELECT COUNT(*) FROM cities", False, None),
    "first_trips": ("01-why-databases/q2.sql", "SELECT id, departs_at FROM trips ORDER BY id LIMIT 5", True, None),
    # chapter 2: asking for rows
    "q_paid_coffee": ("02-asking-for-rows/q1.sql",
                      "SELECT seat_no, passenger_id FROM bookings WHERE trip_id = 42 AND status = 'confirmed' ORDER BY seat_no",
                      True, None),
    "q_count_refunds": ("02-asking-for-rows/q2.sql", "SELECT COUNT(*) AS cancelled FROM bookings WHERE status = 'cancelled'",
                        False, ["cancelled"]),
    # chapter 3: sorting and shaping
    "longest_routes": ("03-sorting-and-shaping/q1.sql",
                       "SELECT id, distance_km FROM routes ORDER BY distance_km DESC, id LIMIT 3", True, None),
    "distinct_operators": ("03-sorting-and-shaping/q2.sql", "SELECT DISTINCT operator FROM buses ORDER BY operator", True, None),
    # chapter 4: text, numbers, dates and NULL
    "night_trips": ("04-text-dates-null/q1.sql",
                    "SELECT id, departs_at FROM trips WHERE departs_at >= '2026-11-15 21:00' AND departs_at < '2026-11-16' "
                    "ORDER BY departs_at", True, None),
    "missing_emails": ("04-text-dates-null/q2.sql", "SELECT COUNT(*) FROM passengers WHERE email IS NULL", False, None),
    # chapter 5: joins
    "route_names": ("05-joins/q1.sql",
        'SELECT r.id, f.name, t.name FROM routes r JOIN cities f ON f.id = r.from_city_id JOIN cities t ON t.id = r.to_city_id ORDER BY r.id',
        True, None),
    "never_booked": ("05-joins/q2.sql",
        'SELECT p.id, p.name FROM passengers p LEFT JOIN bookings b ON b.passenger_id = p.id WHERE b.id IS NULL ORDER BY p.id',
        True, None),
    # chapter 6: totals
    "q_revenue_by_outlet": ("06-totals/q1.sql",
        "SELECT bu.operator, SUM(b.amount_paise) FROM bookings b JOIN trips t ON t.id = b.trip_id JOIN buses bu ON bu.id = t.bus_id WHERE b.status = 'confirmed' GROUP BY bu.operator ORDER BY 2 DESC",
        True, None),
    "q_top_item": ("06-totals/q2.sql",
        "SELECT t.route_id, COUNT(*) FROM bookings b JOIN trips t ON t.id = b.trip_id WHERE b.status = 'confirmed' GROUP BY t.route_id ORDER BY 2 DESC LIMIT 1",
        True, None),
    # chapter 7: subqueries and CTEs
    "above_average": ("07-subqueries-and-ctes/q1.sql",
        'SELECT id, distance_km FROM routes WHERE distance_km > (SELECT AVG(distance_km) FROM routes) ORDER BY id',
        True, None),
    "almost_full": ("07-subqueries-and-ctes/q2.sql",
        "WITH sold AS (SELECT t.id, bu.seats, COUNT(b.id) AS confirmed FROM trips t JOIN buses bu ON bu.id = t.bus_id LEFT JOIN bookings b ON b.trip_id = t.id AND b.status = 'confirmed' GROUP BY t.id, bu.seats) SELECT COUNT(*) FROM sold WHERE confirmed >= 0.9 * seats",
        False, None),
    # chapter 8: window functions
    "rank_operators": ("08-window-functions/q1.sql",
        "SELECT bu.operator, SUM(b.amount_paise), RANK() OVER (ORDER BY SUM(b.amount_paise) DESC) FROM bookings b JOIN trips t ON t.id = b.trip_id JOIN buses bu ON bu.id = t.bus_id WHERE b.status = 'confirmed' GROUP BY bu.operator ORDER BY 3",
        True, None),
    "running_total": ("08-window-functions/q2.sql",
        "SELECT t.departs_at::date, SUM(b.amount_paise), SUM(SUM(b.amount_paise)) OVER (ORDER BY t.departs_at::date) FROM bookings b JOIN trips t ON t.id = b.trip_id WHERE b.status = 'confirmed' GROUP BY 1 ORDER BY 1",
        True, None),
    # chapter 14: capstone
    "monthly_report": ("14-capstone/q1.sql",
        "WITH t AS (SELECT route_id, COUNT(*) AS trips FROM trips WHERE departs_at < '2026-12-01' GROUP BY route_id), "
        "b AS (SELECT t.route_id, COUNT(*) AS bookings, SUM(b.amount_paise) AS revenue FROM bookings b JOIN trips t ON t.id = b.trip_id "
        "WHERE b.status = 'confirmed' AND t.departs_at < '2026-12-01' GROUP BY t.route_id) "
        "SELECT r.id, f.name, c.name, t.trips, COALESCE(b.bookings, 0), COALESCE(b.revenue, 0) FROM routes r "
        "JOIN cities f ON f.id = r.from_city_id JOIN cities c ON c.id = r.to_city_id JOIN t ON t.route_id = r.id "
        "LEFT JOIN b ON b.route_id = r.id ORDER BY 6 DESC, r.id",
        True, None),
    "top_passengers": ("14-capstone/q2.sql",
        "SELECT p.name, COUNT(*), SUM(b.amount_paise), RANK() OVER (ORDER BY SUM(b.amount_paise) DESC) FROM bookings b "
        "JOIN passengers p ON p.id = b.passenger_id WHERE b.status = 'confirmed' GROUP BY p.id, p.name "
        "ORDER BY 3 DESC, p.id LIMIT 5",
        True, None),
}


def report(task, passed, message, expected=None, actual=None):
    r = {"task": task, "passed": passed, "message": message}
    if expected is not None:
        r["expected"], r["actual"] = expected, actual
    print("@@RESULT " + json.dumps(r, default=str), flush=True)


def run(conn, sql):
    """One statement, read-only, at most 5 seconds; returns (column names, rows)."""
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute("SET LOCAL statement_timeout = '5s'")
            cur.execute(sql)
            if cur.description is None:
                raise ValueError("the query returned no rows (is it a SELECT?)")
            return [d.name for d in cur.description], [tuple(norm(v) for v in r) for r in cur.fetchall()]


def norm(v):
    """Numbers compare by value: 25 and 25.00 are the same answer."""
    if isinstance(v, Decimal):
        return float(v)
    return v


def short(rows):
    return json.dumps([list(r) for r in rows[:3]], default=str) + (" ..." if len(rows) > 3 else "")


def query_body(file):
    path = WS / file
    sql = path.read_text(encoding="utf-8") if path.is_file() else ""
    lines = [l for l in sql.splitlines() if not l.strip().startswith("--")]
    return "\n".join(lines).strip().rstrip(";").strip()


def check_query(conn, task, file, reference, ordered, names):
    body = query_body(file)
    if not body or body.upper() == "SELECT 1":
        return report(task, False, f"Write your query in {file}, below the comment, then run it with psql -f.")
    if ";" in body:
        return report(task, False, f"{file} should hold one query (remove the extra statements).")
    try:
        _, want = run(conn, reference)
    except Exception as e:
        return report(task, False, f"The Safar data is missing or changed ({str(e).splitlines()[0]}). Press Reset lab.")
    try:
        cols, got = run(conn, body)
    except Exception as e:
        msg = str(e).splitlines()[0]
        hint = " Text values need single quotes: 'confirmed'." if "column" in msg and "does not exist" in msg else ""
        return report(task, False, f"{file} failed: {msg}.{hint}")
    want_cols = len(want[0]) if want else len(cols)
    if len(cols) != want_cols:
        return report(task, False, f"{file} returns {len(cols)} column(s); the answer has {want_cols}.",
                      f"{want_cols} columns", f"{len(cols)} columns: {', '.join(cols)}")
    if names and [c.lower() for c in cols] != names:
        return report(task, False, "The answer is right, but name the column as the task asks (with AS).",
                      ", ".join(names), ", ".join(cols))
    if len(got) != len(want):
        return report(task, False, f"{file} returns {len(got)} row(s); the answer has {len(want)}. Check the filter.",
                      f"{len(want)} rows", f"{len(got)} rows")
    if not ordered:
        got, want = sorted(got, key=str), sorted(want, key=str)
    if got != want:
        if ordered and sorted(got, key=str) == sorted(want, key=str):
            return report(task, False, f"{file} returns the right rows, in the wrong order. Check ORDER BY.",
                          short(want), short(got))
        first = next(i for i, (a, b) in enumerate(zip(got, want)) if a != b)
        return report(task, False, f"Row {first + 1} of {file} is different (check the filter and the columns).",
                      short(want[first:]), short(got[first:]))
    report(task, True, f"{len(got)} row(s), all correct.")


# ---------- chapters 9 to 11: tasks that change data, checked by the database's state ----------

def one(conn, sql, *args):
    with conn.cursor() as cur:
        cur.execute(sql, args)
        row = cur.fetchone()
        return row[0] if row else None


def refused(conn, sql, *args):
    """Run a statement inside a transaction that is always rolled back; return the error's SQLSTATE or None."""
    try:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(sql, args)
            raise _Rollback()
    except _Rollback:
        return None
    except psycopg.Error as e:
        return e.sqlstate or "error"


class _Rollback(Exception):
    pass


def columns(conn, table):
    with conn.cursor() as cur:
        cur.execute("SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns "
                    "WHERE table_schema = 'public' AND table_name = %s", (table,))
        return {r[0]: r[1:] for r in cur.fetchall()}


def reviews_table(conn):
    t = "reviews_table"
    cols = columns(conn, "reviews")
    if not cols:
        return report(t, False, "There is no table called reviews yet. Write the CREATE TABLE in 09-tables-and-constraints/reviews.sql and run it with psql -f.")
    want = ["id", "booking_id", "stars", "comment", "created_at"]
    missing = [c for c in want if c not in cols]
    if missing:
        return report(t, False, f"reviews has no column {missing[0]}.", ", ".join(want), ", ".join(cols))
    pk = one(conn, "SELECT string_agg(a.attname, ',') FROM pg_index i JOIN pg_attribute a ON a.attrelid = i.indrelid "
             "AND a.attnum = ANY(i.indkey) WHERE i.indrelid = 'reviews'::regclass AND i.indisprimary")
    if pk != "id":
        return report(t, False, "id should be the primary key of reviews.", "PRIMARY KEY (id)", pk or "no primary key")
    fk = one(conn, "SELECT confrelid::regclass::text FROM pg_constraint WHERE conrelid = 'reviews'::regclass AND contype = 'f'")
    if fk != "bookings":
        return report(t, False, "booking_id should be a foreign key to bookings, so a review can only be about a real booking.",
                      "REFERENCES bookings(id)", fk or "no foreign key")
    if cols["booking_id"][1] != "NO" or cols["stars"][1] != "NO":
        return report(t, False, "booking_id and stars must be NOT NULL: a review always has both.")
    if cols["created_at"][2] is None:
        return report(t, False, "created_at should fill itself in: give it a DEFAULT (now()).", "DEFAULT now()", "no default")
    if refused(conn, "INSERT INTO reviews (booking_id, stars) VALUES (1, 4)") is not None:
        return report(t, False, "A normal review (booking 1, 4 stars) was refused. Let id and created_at fill themselves in.")
    for stars in (0, 6):
        if refused(conn, "INSERT INTO reviews (booking_id, stars) VALUES (1, %s)", stars) != "23514":
            return report(t, False, f"A review with {stars} stars was accepted. Add a CHECK so stars is from 1 to 5.",
                          "refused", "accepted")
    if refused(conn, "INSERT INTO reviews (booking_id, stars) VALUES (99999999, 4)") != "23503":
        return report(t, False, "A review of a booking that does not exist was accepted.", "refused", "accepted")
    report(t, True, "reviews is ready: real bookings only, 1 to 5 stars, ids and times filled in by the database.")


def one_seat_one_booking(conn):
    t = "one_seat_one_booking"
    if one(conn, "SELECT to_regclass('bookings')") is None:
        return report(t, False, "The bookings table is missing. Press Reset lab.")
    state = refused(conn, "INSERT INTO bookings (id, trip_id, passenger_id, seat_no, status, booked_at, amount_paise) "
                    "SELECT 99999998, trip_id, 1, seat_no, 'confirmed', now(), amount_paise FROM bookings WHERE id = 936")
    if state is None:
        return report(t, False, "A second booking for trip 42, seat 1 was accepted. Add a UNIQUE constraint on the trip and the seat.",
                      "refused", "accepted")
    if state != "23505":
        return report(t, False, f"A duplicate seat was refused, but not by a unique constraint (error {state}).")
    report(t, True, "Two bookings can never take the same seat on the same trip: the database itself refuses.")


def add_trip(conn):
    t = "add_trip"
    row = None
    with conn.cursor() as cur:
        cur.execute("SELECT route_id, bus_id, departs_at, fare_paise FROM trips WHERE id = 481")
        row = cur.fetchone()
    if row is None:
        return report(t, False, "There is no trip 481 yet. Write the INSERT in 10-changing-data/add_trip.sql and run it.")
    want = (1, 1, "2026-12-01 09:00:00", 33000)
    got = (row[0], row[1], str(row[2]), row[3])
    if got != want:
        return report(t, False, "Trip 481 is there, but some values are different.", json.dumps(want), json.dumps(got))
    report(t, True, "Trip 481, Pune to Mumbai on 1 December at 09:00, is on sale.")


def raise_fares(conn):
    t = "raise_fares"
    with conn.cursor() as cur:
        cur.execute("SELECT departs_at >= '2026-11-20' AS late, array_agg(DISTINCT fare_paise) FROM trips "
                    "WHERE route_id = 7 GROUP BY 1")
        fares = {late: sorted(f) for late, f in cur.fetchall()}
        cur.execute("SELECT COUNT(*) FROM trips WHERE route_id <> 7 AND fare_paise <> "
                    "(SELECT r.distance_km * CASE b.kind WHEN 'AC sleeper' THEN 220 WHEN 'AC seater' THEN 160 ELSE 110 END / 100 * 100 "
                    "FROM routes r JOIN buses b ON b.id = r.id WHERE r.id = trips.route_id)")
        others = cur.fetchone()[0]
    if fares.get(True) == [64900]:
        return report(t, False, "Route 7's fares from 20 November are still 64900 paise.", "71390", "64900")
    if fares.get(False) != [64900]:
        return report(t, False, "Fares before 20 November changed too. Only trips from 20 November should go up.",
                      "64900 before the 20th", json.dumps(fares.get(False)))
    if fares.get(True) != [71390]:
        return report(t, False, "Route 7's fares from 20 November should be 10% higher than 64900.", "71390", json.dumps(fares.get(True)))
    if others:
        return report(t, False, f"{others} trip(s) on other routes changed fare. Did the UPDATE's WHERE miss the route?")
    report(t, True, "11 trips on route 7 went up by 10%, and nothing else changed.")


def move_booking(conn):
    t = "move_booking"
    old = one(conn, "SELECT status FROM bookings WHERE id = 936")
    new = None
    with conn.cursor() as cur:
        cur.execute("SELECT id, passenger_id, seat_no, status, amount_paise FROM bookings WHERE trip_id = 74")
        new = cur.fetchall()
    if old is None:
        return report(t, False, "Booking 936 has been deleted. Cancel it instead (status 'cancelled'); Reset lab brings it back.")
    if old == "confirmed" and not new:
        return report(t, False, "Booking 936 is still confirmed on trip 42, and nothing is booked on trip 74 yet.")
    if old == "confirmed":
        return report(t, False, "Trip 74 has the new booking, but booking 936 is still confirmed: the passenger now holds two seats.",
                      "936 cancelled", "936 confirmed")
    if not new:
        return report(t, False, "Booking 936 was cancelled, but no booking was made on trip 74: the passenger lost the seat.",
                      "a booking on trip 74", "none")
    if len(new) != 1 or new[0][1] != 398 or new[0][2] != 1 or new[0][3] != "confirmed":
        return report(t, False, "Trip 74 should have one confirmed booking: passenger 398, seat 1.", "[398, seat 1, confirmed]",
                      json.dumps([[r[1], r[2], r[3]] for r in new]))
    fare = one(conn, "SELECT fare_paise FROM trips WHERE id = 74")
    if new[0][4] != fare:
        return report(t, False, "The new booking's amount should be trip 74's fare.", str(fare), str(new[0][4]))
    report(t, True, "Passenger 398 moved from trip 42 to trip 74 in one step: never two seats, never none.")


def refund_trip(conn):
    t = "refund_trip"
    confirmed = one(conn, "SELECT COUNT(*) FROM bookings WHERE trip_id = 100 AND status = 'confirmed'")
    total = one(conn, "SELECT COUNT(*) FROM bookings WHERE trip_id = 100")
    if total == 0:
        return report(t, False, "Trip 100's bookings were deleted. Cancel them instead, so the refunds stay on record (Reset lab restores them).")
    if confirmed:
        return report(t, False, f"Trip 100 still has {confirmed} confirmed booking(s).", "0", str(confirmed))
    if one(conn, "SELECT COUNT(*) FROM bookings WHERE trip_id = 101 AND status = 'confirmed'") != 35:
        return report(t, False, "Bookings on other trips changed too. Only trip 100 was called off.")
    report(t, True, "Every booking on trip 100 is cancelled, and nothing else changed.")


WRITES = [reviews_table, one_seat_one_booking, add_trip, raise_fares, move_booking, refund_trip]


# ---------- chapter 12: indexes ----------

def index_columns(conn, table):
    """Every index on the table as a list of its column names, in order."""
    with conn.cursor() as cur:
        cur.execute("SELECT i.indexrelid::regclass::text, array_agg(a.attname ORDER BY k.n) FROM pg_index i "
                    "CROSS JOIN LATERAL unnest(i.indkey) WITH ORDINALITY AS k(attnum, n) "
                    "JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = k.attnum "
                    "WHERE i.indrelid = %s::regclass GROUP BY 1", (table,))
        return {name: cols for name, cols in cur.fetchall()}


def plan_uses_index(conn, sql):
    with conn.cursor() as cur:
        cur.execute("EXPLAIN (FORMAT JSON) " + sql)
        return "Index" in json.dumps(cur.fetchone()[0])


def index_passenger(conn):
    t = "index_passenger"
    if one(conn, "SELECT to_regclass('searches')") is None:
        return report(t, False, "The searches table is missing. Open chapter 12 again, or press Reset lab.")
    idx = index_columns(conn, "searches")
    if not any(cols[0] == "passenger_id" for cols in idx.values()):
        return report(t, False, "There is no index on searches that starts with passenger_id yet.",
                      "an index on (passenger_id)", ", ".join(f"{n} {c}" for n, c in idx.items()))
    if not plan_uses_index(conn, "SELECT * FROM searches WHERE passenger_id = 42"):
        return report(t, False, "The index exists, but the plan for a passenger's searches does not use it. Run ANALYZE searches; and look again.")
    report(t, True, "A passenger's 1,000 searches now come from the index: about a hundred times faster than reading two million rows.")


def index_trip_search(conn):
    t = "index_trip_search"
    if one(conn, "SELECT to_regclass('searches')") is None:
        return report(t, False, "The searches table is missing. Open chapter 12 again, or press Reset lab.")
    want = {"from_city_id", "to_city_id", "travel_date"}
    idx = index_columns(conn, "searches")
    if not any(set(cols[:3]) == want for cols in idx.values()):
        single = [n for n, c in idx.items() if len(c) == 1 and c[0] in want]
        why = " One index per column is not the same: the search needs all three together, in one index." if single else ""
        return report(t, False, "There is no index that starts with from_city_id, to_city_id and travel_date." + why,
                      "one index on all three columns", ", ".join(f"{n} {c}" for n, c in idx.items()))
    if not plan_uses_index(conn, "SELECT * FROM searches WHERE from_city_id = 1 AND to_city_id = 2 AND travel_date = '2026-11-20'"):
        return report(t, False, "The index exists, but the plan for the trip search does not use it. Run ANALYZE searches; and look again.")
    report(t, True, "The app's trip search now uses one index for all three conditions: milliseconds instead of a full scan.")


WRITES += [index_passenger, index_trip_search]


# ---------- chapter 13: designing tables ----------

def operators_table(conn):
    t = "operators_table"
    cols = columns(conn, "operators")
    if not cols:
        return report(t, False, "There is no table called operators yet. Write it in 13-designing-tables/operators.sql and run it.")
    if "id" not in cols or "name" not in cols:
        return report(t, False, "operators needs an id and a name column.", "id, name", ", ".join(cols))
    with conn.cursor() as cur:
        cur.execute("SELECT name FROM operators ORDER BY name")
        names = [r[0] for r in cur.fetchall()]
        cur.execute("SELECT DISTINCT operator FROM buses ORDER BY operator")
        want = [r[0] for r in cur.fetchall()]
    if names != want:
        return report(t, False, "operators should hold each operator name from buses exactly once.", json.dumps(want), json.dumps(names))
    if refused(conn, "INSERT INTO operators (name) VALUES ('Konkan Lines')") != "23505":
        return report(t, False, "A second 'Konkan Lines' was accepted. An operator's name must be UNIQUE.", "refused", "accepted")
    report(t, True, f"{len(names)} operators, each stored once.")


def buses_operator_id(conn):
    t = "buses_operator_id"
    if not columns(conn, "operators"):
        return report(t, False, "Make the operators table first (the task before this one).")
    cols = columns(conn, "buses")
    if "operator_id" not in cols:
        return report(t, False, "buses has no operator_id column yet.")
    fk = one(conn, "SELECT confrelid::regclass::text FROM pg_constraint WHERE conrelid = 'buses'::regclass AND contype = 'f' "
             "AND conkey = ARRAY[(SELECT attnum FROM pg_attribute WHERE attrelid = 'buses'::regclass AND attname = 'operator_id')]::smallint[]")
    if fk != "operators":
        return report(t, False, "operator_id should be a foreign key to operators.", "REFERENCES operators(id)", fk or "no foreign key")
    empty = one(conn, "SELECT COUNT(*) FROM buses WHERE operator_id IS NULL")
    if empty:
        return report(t, False, f"{empty} bus(es) have no operator_id yet. Fill it in from the operator's name.", "0", str(empty))
    wrong = one(conn, "SELECT COUNT(*) FROM buses b JOIN operators o ON o.id = b.operator_id WHERE o.name <> b.operator")
    if wrong:
        return report(t, False, f"{wrong} bus(es) point at the wrong operator.", "0", str(wrong))
    if cols["operator_id"][1] != "NO":
        return report(t, False, "Every bus is filled in; now make operator_id NOT NULL, so a new bus can never miss it.")
    report(t, True, "Every bus points at its operator by id. Renaming an operator now changes one row.")


WRITES += [operators_table, buses_operator_id]


try:
    conn = psycopg.connect(host="db", user="postgres", password="labpass", dbname="safar", connect_timeout=5, autocommit=True)
except Exception as e:
    for t in sorted(WANTED) or sorted(QUERIES) + [w.__name__ for w in WRITES]:
        report(t, False, f"Could not connect to the database: {e}")
    raise SystemExit(0)

for task, spec in QUERIES.items():
    if not WANTED or task in WANTED:
        check_query(conn, task, *spec)

for check in WRITES:
    if not WANTED or check.__name__ in WANTED:
        try:
            check(conn)
        except psycopg.Error as e:
            report(check.__name__, False, f"The database answered an error: {str(e).splitlines()[0]}. Reset lab if the tables are broken.")
