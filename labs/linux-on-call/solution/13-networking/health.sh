#!/usr/bin/env bash
# health.sh URL: is this service healthy?
#   it answers with HTTP status 200 within 3 seconds -> print "UP",   exit code 0
#   anything else (no answer, an error status, slow) -> print "DOWN", exit code 1
status=$(curl -s -o /dev/null --max-time 3 -w '%{http_code}' "$1")
if [ "$status" = 200 ]; then
  echo UP
else
  echo DOWN
  exit 1
fi
