-- move_booking (task move_booking): passenger 398 wants to move from trip 42 (booking 936, seat 1) to trip 74,
-- two days later, seat 1. Cancel the old booking and make the new one (id 12006) as ONE transaction, so the
-- passenger never ends up with two seats or none. Run it with:  psql -f move_booking.sql

BEGIN;
UPDATE bookings SET status = 'cancelled' WHERE id = 936;
INSERT INTO bookings (id, trip_id, passenger_id, seat_no, status, booked_at, amount_paise)
SELECT 12006, 74, 398, 1, 'confirmed', now(), fare_paise FROM trips WHERE id = 74;
COMMIT;
