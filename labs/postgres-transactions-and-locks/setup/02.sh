#!/usr/bin/env bash
# Chapter 2 setup: today's orders, then the incident. A "nightly report" opened a transaction, locked
# order 42, and never committed. It runs as root, so the learner cannot simply kill the process.
set -euo pipefail
psql -v ON_ERROR_STOP=1 -q <<'SQL'
DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
  id           integer PRIMARY KEY,
  item         text    NOT NULL,
  status       text    NOT NULL DEFAULT 'pending'
);
INSERT INTO orders (id, item)
SELECT n, (ARRAY['novel', 'atlas', 'comic', 'diary'])[1 + n % 4]
FROM generate_series(1, 100) AS n;
ALTER DATABASE shop RESET idle_in_transaction_session_timeout;
SQL
PGAPPNAME=nightly-report setsid nohup bash -c \
  '(echo "BEGIN; UPDATE orders SET item = item WHERE id = 42;"; sleep 86400) | psql -q' \
  > /dev/null 2>&1 < /dev/null &
# Wait until the lock is really held.
for _ in $(seq 1 50); do
  n=$(psql -tAc "SELECT count(*) FROM pg_stat_activity WHERE application_name = 'nightly-report' AND state = 'idle in transaction'")
  [ "$n" = "1" ] && exit 0
  sleep 0.2
done
echo "the blocking session did not start" >&2
exit 1
