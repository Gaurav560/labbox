#!/usr/bin/env bash
# watchdog.sh: keep the Tara observatory app alive. Run it every minute from cron.
#   if http://localhost:8090/health answers 200 -> do nothing at all
#   otherwise -> start the app again with app/start.sh, and add one line to watchdog.log:
#                "YYYY-MM-DD HH:MM:SS restarted the app"
# It must work from any folder (cron does not start in this one).
cd /workspace/15-capstone
if curl -sf --max-time 3 -o /dev/null http://localhost:8090/health; then
  exit 0
fi
./app/start.sh > /dev/null
echo "$(date '+%Y-%m-%d %H:%M:%S') restarted the app" >> watchdog.log
