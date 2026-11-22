-- q1 (task above_average): Routes longer than the average route: id and distance_km, by id.
-- Write one query below, then run it from this folder:  psql -f q1.sql

SELECT id, distance_km
FROM routes
WHERE distance_km > (SELECT AVG(distance_km) FROM routes)
ORDER BY id;
