-- q1 (task rank_operators): Rank the operators by confirmed revenue: operator, revenue_paise and rank (1 = most), by rank.
-- Write one query below, then run it from this folder:  psql -f q1.sql

SELECT bu.operator, SUM(b.amount_paise) AS revenue_paise,
       RANK() OVER (ORDER BY SUM(b.amount_paise) DESC) AS rank
FROM bookings b
JOIN trips t ON t.id = b.trip_id
JOIN buses bu ON bu.id = t.bus_id
WHERE b.status = 'confirmed'
GROUP BY bu.operator
ORDER BY rank;
