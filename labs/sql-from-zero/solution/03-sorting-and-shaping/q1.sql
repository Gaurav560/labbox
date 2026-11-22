-- q1 (task longest_routes): The three longest routes: id and distance_km, longest first (equal distances by id).
-- Write one query below, then run it from this folder:  psql -f q1.sql

SELECT id, distance_km
FROM routes
ORDER BY distance_km DESC, id
LIMIT 3;
