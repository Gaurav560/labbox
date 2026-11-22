-- q2 (task top_passengers): Safar's five best customers by confirmed spend: name, trips (confirmed bookings),
-- spent_paise and rank (1 = spent the most), most first; equal spends by passenger id. Run it with:  psql -f q2.sql

SELECT p.name, COUNT(*) AS trips, SUM(b.amount_paise) AS spent_paise,
       RANK() OVER (ORDER BY SUM(b.amount_paise) DESC) AS rank
FROM bookings b
JOIN passengers p ON p.id = b.passenger_id
WHERE b.status = 'confirmed'
GROUP BY p.id, p.name
ORDER BY spent_paise DESC, p.id
LIMIT 5;
