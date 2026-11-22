-- q1 (task route_names): Every route with its city names: the route id, from_city and to_city, by route id.
-- Write one query below, then run it from this folder:  psql -f q1.sql

SELECT r.id, f.name AS from_city, t.name AS to_city
FROM routes r
JOIN cities f ON f.id = r.from_city_id
JOIN cities t ON t.id = r.to_city_id
ORDER BY r.id;
