-- q2 (task running_total): Confirmed revenue for each day of November (by departure day), with a running total: day, revenue_paise, running_total, by day.
-- Write one query below, then run it from this folder:  psql -f q2.sql

SELECT t.departs_at::date AS day,
       SUM(b.amount_paise) AS revenue_paise,
       SUM(SUM(b.amount_paise)) OVER (ORDER BY t.departs_at::date) AS running_total
FROM bookings b
JOIN trips t ON t.id = b.trip_id
WHERE b.status = 'confirmed'
GROUP BY day
ORDER BY day;
