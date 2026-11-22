-- trip_search_index (task index_trip_search): make the app's search fast: searches from one city to another
-- for one travel date. Run it with:  psql -f trip_search_index.sql

CREATE INDEX searches_trip_idx ON searches (from_city_id, to_city_id, travel_date);
