-- one_seat (task one_seat_one_booking): make it impossible for two bookings to take the same seat on the same
-- trip. Run it with:  psql -f one_seat.sql

ALTER TABLE bookings ADD CONSTRAINT one_booking_per_seat UNIQUE (trip_id, seat_no);
