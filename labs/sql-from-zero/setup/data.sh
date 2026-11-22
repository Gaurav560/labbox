#!/usr/bin/env bash
# Safar, a bus ticket booking app: cities, routes, buses, trips, passengers and bookings for November 2026.
# Deterministic (setseed), so every learner and every check sees the same rows. Running it again resets the data
# to exactly this state (chapters 9 to 11 change data, and Reset lab brings it back).
set -euo pipefail
# The database is called safar. Machines made before the course was rewritten have only the old one: create it.
if ! psql -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = 'safar'" | grep -q 1; then
  psql -d postgres -q -c "CREATE DATABASE safar"
fi
export PGDATABASE=safar
psql -v ON_ERROR_STOP=1 -q <<'SQL'
SET client_min_messages TO warning;
DROP TABLE IF EXISTS bookings, passengers, trips, buses, routes, cities CASCADE;

CREATE TABLE cities (
  id    integer PRIMARY KEY,
  name  text NOT NULL UNIQUE,
  state text NOT NULL
);
INSERT INTO cities VALUES
  (1, 'Pune', 'Maharashtra'), (2, 'Mumbai', 'Maharashtra'), (3, 'Nagpur', 'Maharashtra'),
  (4, 'Kolhapur', 'Maharashtra'), (5, 'Panaji', 'Goa'), (6, 'Bengaluru', 'Karnataka'),
  (7, 'Hyderabad', 'Telangana'), (8, 'Chennai', 'Tamil Nadu');

CREATE TABLE routes (
  id           integer PRIMARY KEY,
  from_city_id integer NOT NULL REFERENCES cities(id),
  to_city_id   integer NOT NULL REFERENCES cities(id),
  distance_km  integer NOT NULL
);
INSERT INTO routes VALUES
  (1, 1, 2, 150), (2, 2, 1, 150), (3, 1, 4, 230), (4, 4, 1, 230), (5, 1, 5, 450), (6, 5, 1, 450),
  (7, 2, 5, 590), (8, 5, 2, 590), (9, 1, 3, 710), (10, 3, 1, 710), (11, 1, 7, 560), (12, 7, 1, 560),
  (13, 6, 8, 350), (14, 8, 6, 350), (15, 1, 6, 840), (16, 6, 1, 840);

CREATE TABLE buses (
  id       integer PRIMARY KEY,
  operator text NOT NULL,
  kind     text NOT NULL,
  seats    integer NOT NULL
);
INSERT INTO buses VALUES
  (1, 'Sahyadri Travels', 'AC sleeper', 30), (2, 'Sahyadri Travels', 'AC seater', 40),
  (3, 'Deccan Rides', 'AC sleeper', 30), (4, 'Deccan Rides', 'non-AC seater', 45),
  (5, 'Konkan Lines', 'AC seater', 40), (6, 'Konkan Lines', 'AC sleeper', 30),
  (7, 'Godavari Coaches', 'non-AC seater', 45), (8, 'Godavari Coaches', 'AC seater', 40),
  (9, 'Kaveri Travels', 'AC sleeper', 30), (10, 'Kaveri Travels', 'AC seater', 40),
  (11, 'Sahyadri Travels', 'AC seater', 40), (12, 'Deccan Rides', 'AC sleeper', 30),
  (13, 'Konkan Lines', 'non-AC seater', 45), (14, 'Godavari Coaches', 'AC sleeper', 30),
  (15, 'Kaveri Travels', 'non-AC seater', 45), (16, 'Sahyadri Travels', 'AC sleeper', 30);

-- One trip a day on every route, all of November 2026. Bus i runs route i. Times are India time.
CREATE TABLE trips (
  id         integer PRIMARY KEY,
  route_id   integer NOT NULL REFERENCES routes(id),
  bus_id     integer NOT NULL REFERENCES buses(id),
  departs_at timestamp NOT NULL,
  fare_paise integer NOT NULL
);
SELECT setseed(0.42) \g /dev/null
INSERT INTO trips
SELECT (d - 1) * 16 + r.id,
       r.id,
       r.id,
       timestamp '2026-11-01' + (d - 1) * interval '1 day'
         + (ARRAY[interval '06:30', interval '09:00', interval '13:15', interval '21:30', interval '22:45', interval '23:30'])
           [1 + (r.id % 6)],
       (r.distance_km * CASE b.kind WHEN 'AC sleeper' THEN 220 WHEN 'AC seater' THEN 160 ELSE 110 END / 100) * 100
FROM generate_series(1, 30) AS d
CROSS JOIN routes r
JOIN buses b ON b.id = r.id;

CREATE TABLE passengers (
  id      integer PRIMARY KEY,
  name    text NOT NULL,
  phone   text NOT NULL,
  email   text,
  city_id integer NOT NULL REFERENCES cities(id)
);
INSERT INTO passengers
SELECT g,
       (ARRAY['Asha', 'Ravi', 'Meera', 'Kabir', 'Priya', 'Dev', 'Sana', 'Arjun', 'Zoya', 'Ishaan', 'Nisha', 'Rohan',
              'Tara', 'Vikram', 'Anjali', 'Farhan', 'Kavya', 'Neel', 'Pooja', 'Siddharth'])[1 + (g * 7) % 20]
         || ' ' ||
       (ARRAY['Sharma', 'Patil', 'Iyer', 'Khan', 'Reddy', 'Desai', 'Nair', 'Joshi', 'Kulkarni', 'Rao', 'Gupta',
              'Menon', 'Shaikh', 'Pillai', 'Bose'])[1 + (g * 11) % 15],
       '98' || lpad(((g * 7919) % 100000000)::text, 8, '0'),
       CASE WHEN g % 7 = 0 THEN NULL ELSE 'p' || g || '@example.com' END,
       1 + (g * 13) % 8
FROM generate_series(1, 2000) AS g;

CREATE TABLE bookings (
  id           integer PRIMARY KEY,
  trip_id      integer NOT NULL REFERENCES trips(id),
  passenger_id integer NOT NULL REFERENCES passengers(id),
  seat_no      integer NOT NULL,
  status       text NOT NULL,
  booked_at    timestamp NOT NULL,
  amount_paise integer NOT NULL
);
-- Every trip sells a share of its seats; about one booking in eight is cancelled.
INSERT INTO bookings (id, trip_id, passenger_id, seat_no, status, booked_at, amount_paise)
SELECT row_number() OVER (ORDER BY t.id, s),
       t.id,
       1 + floor(random() * 2000)::int,
       s,
       CASE WHEN random() < 0.125 THEN 'cancelled' ELSE 'confirmed' END,
       t.departs_at - (1 + floor(random() * 14)::int) * interval '1 day' - floor(random() * 1440)::int * interval '1 minute',
       t.fare_paise
FROM trips t
JOIN buses b ON b.id = t.bus_id
CROSS JOIN generate_series(1, 45) AS s
WHERE s <= b.seats AND random() < 0.55 + 0.25 * (t.route_id % 3) / 2.0;
ANALYZE;
SQL
