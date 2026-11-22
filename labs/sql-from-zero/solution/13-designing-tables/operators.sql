-- operators (task operators_table): a table of bus operators, each stored once: an id the database fills in,
-- and a name that must be unique. Fill it with every operator name that appears in buses. Run it with:
--   psql -f operators.sql

CREATE TABLE operators (
  id   integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name text NOT NULL UNIQUE
);
INSERT INTO operators (name) SELECT DISTINCT operator FROM buses ORDER BY operator;
