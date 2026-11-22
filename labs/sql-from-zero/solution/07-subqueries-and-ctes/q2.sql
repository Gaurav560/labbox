-- q2 (task almost_full): How many trips were at least 90% full (confirmed bookings at least 0.9 times the bus's seats)? One number.
-- Write one query below, then run it from this folder:  psql -f q2.sql

WITH sold AS (
  SELECT t.id, bu.seats, COUNT(b.id) AS confirmed
  FROM trips t
  JOIN buses bu ON bu.id = t.bus_id
  LEFT JOIN bookings b ON b.trip_id = t.id AND b.status = 'confirmed'
  GROUP BY t.id, bu.seats
)
SELECT COUNT(*)
FROM sold
WHERE confirmed >= 0.9 * seats;
