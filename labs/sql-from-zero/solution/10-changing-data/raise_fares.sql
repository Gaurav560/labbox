-- raise_fares (task raise_fares): Konkan Lines raised its fares by 10% on route 7, for trips leaving on or after
-- 20 November 2026. Nothing else changes. Look before you change! Run it with:  psql -f raise_fares.sql

UPDATE trips
SET fare_paise = fare_paise * 110 / 100
WHERE route_id = 7 AND departs_at >= '2026-11-20';
