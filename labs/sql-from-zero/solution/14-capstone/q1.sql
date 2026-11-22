-- q1 (task monthly_report): November's report, one row per route: the route id, from_city, to_city, the number of
-- trips it ran in November, its confirmed bookings and its confirmed revenue_paise (0 when it has none), highest
-- revenue first, then by route id. Run it with:  psql -f q1.sql

WITH route_trips AS (
  SELECT route_id, COUNT(*) AS trips
  FROM trips
  WHERE departs_at < '2026-12-01'
  GROUP BY route_id
),
route_sales AS (
  SELECT t.route_id, COUNT(*) AS bookings, SUM(b.amount_paise) AS revenue_paise
  FROM bookings b
  JOIN trips t ON t.id = b.trip_id
  WHERE b.status = 'confirmed' AND t.departs_at < '2026-12-01'
  GROUP BY t.route_id
)
SELECT r.id, f.name AS from_city, c.name AS to_city, rt.trips,
       COALESCE(s.bookings, 0) AS bookings, COALESCE(s.revenue_paise, 0) AS revenue_paise
FROM routes r
JOIN cities f ON f.id = r.from_city_id
JOIN cities c ON c.id = r.to_city_id
JOIN route_trips rt ON rt.route_id = r.id
LEFT JOIN route_sales s ON s.route_id = r.id
ORDER BY revenue_paise DESC, r.id;
