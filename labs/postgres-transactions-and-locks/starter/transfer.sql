-- transfer(from, to, amount): move amount_paise from one customer's wallet to another's, and record
-- it in ledger. All or nothing: if any part fails, nothing may change.
-- Load it (again after every change) with: psql -f transfer.sql
CREATE OR REPLACE FUNCTION transfer(p_from integer, p_to integer, p_amount integer) RETURNS void AS $$
BEGIN
  -- TODO(atomic_transfer)
  RAISE EXCEPTION 'transfer is not written yet';
END;
$$ LANGUAGE plpgsql;
