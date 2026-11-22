#!/usr/bin/env bash
# Used only by `labbox test-lab`: run every script that changes the database, in chapter order. The query files
# (q1.sql, q2.sql) are checked as they are.
set -euo pipefail
cd /workspace
for f in 09-tables-and-constraints/reviews.sql 09-tables-and-constraints/one_seat.sql \
         10-changing-data/add_trip.sql 10-changing-data/raise_fares.sql \
         11-transactions/move_booking.sql 11-transactions/refund_trip.sql \
         12-indexes/passenger_index.sql 12-indexes/trip_search_index.sql \
         13-designing-tables/operators.sql 13-designing-tables/operator_id.sql; do
  psql -q -v ON_ERROR_STOP=1 -f "$f" > /dev/null
done
