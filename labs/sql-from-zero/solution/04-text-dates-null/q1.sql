-- q1 (task night_trips): Trips leaving at 21:00 or later on 15 November 2026: id and departs_at, earliest first.
-- Write one query below, then run it from this folder:  psql -f q1.sql

SELECT id, departs_at
FROM trips
WHERE departs_at >= '2026-11-15 21:00' AND departs_at < '2026-11-16'
ORDER BY departs_at;
