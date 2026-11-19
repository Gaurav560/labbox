#!/usr/bin/env bash
# Tapri Counter sample data: 6 outlets and 5000 orders. Deterministic (setseed), so every learner
# and every check sees the same rows. Runs for each chapter; running it again gives the same data.
set -euo pipefail
psql -v ON_ERROR_STOP=1 -q <<'SQL'
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS outlets;
CREATE TABLE outlets (id integer PRIMARY KEY, name text NOT NULL, city text NOT NULL);
INSERT INTO outlets VALUES
  (1, 'Andheri', 'Mumbai'), (2, 'Koramangala', 'Bengaluru'), (3, 'Connaught Place', 'Delhi'),
  (4, 'Park Street', 'Kolkata'), (5, 'FC Road', 'Pune'), (6, 'Banjara Hills', 'Hyderabad');
CREATE TABLE orders (
  id           integer PRIMARY KEY,
  outlet_id    integer NOT NULL REFERENCES outlets(id),
  item         text    NOT NULL,
  qty          integer NOT NULL,
  amount_paise integer NOT NULL,
  status       text    NOT NULL
);
SELECT setseed(0.42);
INSERT INTO orders
SELECT g,
       1 + floor(random() * 6)::int,
       (ARRAY['cold coffee', 'filter coffee', 'vada pav', 'samosa', 'bun maska', 'poha'])[1 + floor(random() * 6)::int],
       1 + floor(random() * 4)::int,
       0,
       (ARRAY['paid', 'paid', 'paid', 'paid', 'refunded'])[1 + floor(random() * 5)::int]
FROM generate_series(1, 5000) AS g;
UPDATE orders SET amount_paise = qty * CASE item
  WHEN 'cold coffee' THEN 1500 WHEN 'filter coffee' THEN 2000 WHEN 'vada pav' THEN 2500
  WHEN 'samosa' THEN 2000 WHEN 'bun maska' THEN 3000 ELSE 3500 END;
ANALYZE;
SQL
