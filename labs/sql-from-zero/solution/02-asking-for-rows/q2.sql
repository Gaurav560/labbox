-- q2 (task q_count_refunds): How many bookings were cancelled? One number, in a column named cancelled.
-- Write one query below, then run it from this folder:  psql -f q2.sql

SELECT COUNT(*) AS cancelled
FROM bookings
WHERE status = 'cancelled';
