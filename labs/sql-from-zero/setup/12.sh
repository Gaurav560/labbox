#!/usr/bin/env bash
# Chapter 12 setup: two million searches, the big table that indexes are about. Deterministic, like the rest of
# Safar's data. No indexes except the primary key: making them is the chapter.
set -euo pipefail
export PGDATABASE=safar
psql -v ON_ERROR_STOP=1 -q <<'SQL'
SET client_min_messages TO warning;
DROP TABLE IF EXISTS searches;
CREATE TABLE searches (
  id           bigint PRIMARY KEY,
  passenger_id integer NOT NULL,
  from_city_id integer NOT NULL,
  to_city_id   integer NOT NULL,
  travel_date  date NOT NULL,
  searched_at  timestamp NOT NULL
);
SELECT setseed(0.7) \g /dev/null
INSERT INTO searches
SELECT g,
       1 + (g * 7919) % 2000,
       1 + (g * 13) % 8,
       1 + ((g * 13) % 8 + 1 + (g * 5) % 7) % 8,
       date '2026-11-01' + ((g * 31) % 45)::int,
       timestamp '2026-10-15' + (g % 3000000) * interval '1 second'
FROM generate_series(1::bigint, 2000000) AS g;
ANALYZE searches;
SQL
