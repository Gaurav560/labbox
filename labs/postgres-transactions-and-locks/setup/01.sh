#!/usr/bin/env bash
# Chapter 1 setup: loyalty wallets and a ledger. The old app had no guard, so one wallet is negative.
set -euo pipefail
psql -v ON_ERROR_STOP=1 -q <<'SQL'
DROP TABLE IF EXISTS ledger;
DROP TABLE IF EXISTS wallets;
DROP FUNCTION IF EXISTS transfer(int, int, int);
CREATE TABLE wallets (
  customer_id   integer PRIMARY KEY,
  name          text    NOT NULL,
  balance_paise integer NOT NULL
);
CREATE TABLE ledger (
  id            serial      PRIMARY KEY,
  from_customer integer     NOT NULL,
  to_customer   integer     NOT NULL,
  amount_paise  integer     NOT NULL,
  created_at    timestamptz NOT NULL DEFAULT now()
);
INSERT INTO wallets VALUES
  (1, 'Asha', 12000), (2, 'Ravi', 3000), (3, 'Meera', 50000), (4, 'Kabir', 800),
  (5, 'Priya', 0), (6, 'Arjun', 7500), (7, 'Sana', -2500), (8, 'Dev', 1500);
SQL
