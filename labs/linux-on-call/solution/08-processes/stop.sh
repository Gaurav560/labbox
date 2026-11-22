#!/usr/bin/env bash
# stop.sh NAME: stop every process whose name is exactly NAME.
#   1. Ask politely first: send them TERM.
#   2. Give them up to 3 seconds to finish.
#   3. Any that are still running get KILL.
# Careful: this script must never stop itself, or anything with a different name.
name="$1"
pkill -TERM -x "$name" || exit 0      # -x: the exact process name, so this script never matches itself
for _ in 1 2 3 4 5 6; do
  pgrep -x "$name" > /dev/null || exit 0
  sleep 0.5
done
pkill -KILL -x "$name"
