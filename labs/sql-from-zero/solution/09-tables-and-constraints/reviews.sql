-- reviews (task reviews_table): a table for passengers' reviews of their trips. Run it with:  psql -f reviews.sql
-- Columns: id (filled in by the database), booking_id (a real booking, always there), stars (1 to 5, always
-- there), comment (optional text), created_at (filled in with the current time). The lesson shows each piece.

CREATE TABLE reviews (
  id         integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  booking_id integer NOT NULL REFERENCES bookings(id),
  stars      integer NOT NULL CHECK (stars BETWEEN 1 AND 5),
  comment    text,
  created_at timestamp NOT NULL DEFAULT now()
);
