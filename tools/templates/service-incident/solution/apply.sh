#!/usr/bin/env bash
# Used only by `labbox test-lab`: the fix, applied to the running database.
set -euo pipefail
psql -v ON_ERROR_STOP=1 -c "CREATE INDEX IF NOT EXISTS orders_customer_created_idx ON orders (customer_id, created_at DESC);"
