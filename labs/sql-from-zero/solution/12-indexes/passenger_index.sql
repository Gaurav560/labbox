-- passenger_index (task index_passenger): make "all searches of one passenger" fast. Run it with:  psql -f passenger_index.sql

CREATE INDEX searches_passenger_idx ON searches (passenger_id);
