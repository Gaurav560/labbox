#!/usr/bin/env bash
# stop.sh NAME: stop every process whose name is exactly NAME.
#   1. Ask politely first: send them TERM.
#   2. Give them up to 3 seconds to finish.
#   3. Any that are still running get KILL.
# Careful: this script must never stop itself, or anything with a different name.
# TODO (task stop_hog): your commands here. The process name is "$1".
