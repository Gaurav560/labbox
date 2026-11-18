#!/usr/bin/env bash
# Chapter 1 setup: a million orders, then the incident (the customer_id index disappears).
set -euo pipefail
psql -v ON_ERROR_STOP=1 -q <<'SQL'
DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
  id           bigserial PRIMARY KEY,
  customer_id  integer     NOT NULL,
  item         text        NOT NULL,
  amount_paise integer     NOT NULL,
  status       text        NOT NULL,
  created_at   timestamptz NOT NULL
);
INSERT INTO orders (customer_id, item, amount_paise, status, created_at)
SELECT 1 + (random() * 49999)::int,
       (ARRAY['cutting chai', 'masala chai', 'vada pav', 'samosa', 'bun maska', 'poha'])[1 + (random() * 5)::int],
       1000 + (random() * 20000)::int,
       (ARRAY['paid', 'paid', 'paid', 'refunded'])[1 + (random() * 3)::int],
       now() - random() * interval '180 days'
FROM generate_series(1, 1000000);
CREATE INDEX orders_customer_id_idx ON orders (customer_id);
ANALYZE orders;
-- Last night someone "cleaned up unused indexes".
DROP INDEX orders_customer_id_idx;
SQL
