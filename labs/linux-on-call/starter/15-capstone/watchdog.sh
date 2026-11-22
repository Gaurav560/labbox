#!/usr/bin/env bash
# watchdog.sh: keep the Tara observatory app alive. Run it every minute from cron.
#   if http://localhost:8090/health answers 200 -> do nothing at all
#   otherwise -> start the app again with app/start.sh, and add one line to watchdog.log:
#                "YYYY-MM-DD HH:MM:SS restarted the app"
# It must work from any folder (cron does not start in this one).
# TODO (task capstone_watch): your script here.
