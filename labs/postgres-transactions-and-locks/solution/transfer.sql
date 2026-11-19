-- transfer(from, to, amount): move amount_paise from one customer's wallet to another's, and record
-- it in ledger. All or nothing: if any part fails, nothing may change.
-- Load it (again after every change) with: psql -f transfer.sql
CREATE OR REPLACE FUNCTION transfer(p_from integer, p_to integer, p_amount integer) RETURNS void AS $$
BEGIN
  UPDATE wallets SET balance_paise = balance_paise - p_amount WHERE customer_id = p_from;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'no wallet for customer %', p_from;
  END IF;
  UPDATE wallets SET balance_paise = balance_paise + p_amount WHERE customer_id = p_to;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'no wallet for customer %', p_to;
  END IF;
  INSERT INTO ledger (from_customer, to_customer, amount_paise) VALUES (p_from, p_to, p_amount);
END;
$$ LANGUAGE plpgsql;
