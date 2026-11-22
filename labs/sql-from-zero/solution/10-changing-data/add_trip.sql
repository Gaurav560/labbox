-- add_trip (task add_trip): put trip 481 on sale: route 1 (Pune to Mumbai), bus 1, leaving 1 December 2026 at
-- 09:00, fare 33000 paise. Run it with:  psql -f add_trip.sql

INSERT INTO trips (id, route_id, bus_id, departs_at, fare_paise)
VALUES (481, 1, 1, '2026-12-01 09:00', 33000);
