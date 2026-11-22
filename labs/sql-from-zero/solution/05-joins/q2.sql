-- q2 (task never_booked): Passengers who have never booked anything: their id and name, by id.
-- Write one query below, then run it from this folder:  psql -f q2.sql

SELECT p.id, p.name
FROM passengers p
LEFT JOIN bookings b ON b.passenger_id = p.id
WHERE b.id IS NULL
ORDER BY p.id;
