-- q2 (task first_trips): The first five trips by id: their id and departs_at, lowest id first.
-- Write one query below, then run it from this folder:  psql -f q2.sql

SELECT id, departs_at
FROM trips
ORDER BY id
LIMIT 5;
