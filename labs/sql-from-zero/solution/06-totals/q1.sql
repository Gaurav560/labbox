-- q1 (task q_revenue_by_outlet): Confirmed revenue per bus operator, in paise: operator and revenue_paise, biggest first.
-- Write one query below, then run it from this folder:  psql -f q1.sql

SELECT bu.operator, SUM(b.amount_paise) AS revenue_paise
FROM bookings b
JOIN trips t ON t.id = b.trip_id
JOIN buses bu ON bu.id = t.bus_id
WHERE b.status = 'confirmed'
GROUP BY bu.operator
ORDER BY revenue_paise DESC;
