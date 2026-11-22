#!/usr/bin/env bash
# start.sh: print how the app would start, from two environment variables:
#   PORT     (when it is not set: 8080)
#   APP_ENV  (when it is not set: development)
# Exactly this line: Starting Tara on port PORT in APP_ENV mode
echo "Starting Tara on port ${PORT:-8080} in ${APP_ENV:-development} mode"
