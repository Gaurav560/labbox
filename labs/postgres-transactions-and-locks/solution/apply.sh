#!/usr/bin/env bash
# Used only by `labbox test-lab`: both chapters' fixes, applied to the running database.
set -euo pipefail
cd /workspace
psql -v ON_ERROR_STOP=1 -q <<'SQL'
UPDATE wallets SET balance_paise = 0 WHERE balance_paise < 0;
ALTER TABLE wallets ADD CONSTRAINT wallets_balance_not_negative CHECK (balance_paise >= 0);
SQL
psql -v ON_ERROR_STOP=1 -q -f transfer.sql
psql -v ON_ERROR_STOP=1 -q <<'SQL'
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE application_name = 'nightly-report';
ALTER DATABASE tapri SET idle_in_transaction_session_timeout = '60s';
SQL
