-- q2 (task q_top_item): The busiest route: its route_id and its number of confirmed bookings, only the top one.
-- Write one query below, then run it from this folder:  psql -f q2.sql

SELECT t.route_id, COUNT(*) AS bookings
FROM bookings b
JOIN trips t ON t.id = b.trip_id
WHERE b.status = 'confirmed'
GROUP BY t.route_id
ORDER BY bookings DESC
LIMIT 1;
