-- operator_id (task buses_operator_id): give buses an operator_id that points at operators, fill it in for
-- every bus from its operator's name, then make it NOT NULL. Run it with:  psql -f operator_id.sql

ALTER TABLE buses ADD COLUMN operator_id integer REFERENCES operators(id);
UPDATE buses b SET operator_id = o.id FROM operators o WHERE o.name = b.operator;
ALTER TABLE buses ALTER COLUMN operator_id SET NOT NULL;
