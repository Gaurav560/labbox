#!/usr/bin/env bash
# health.sh URL: is this service healthy?
#   it answers with HTTP status 200 within 3 seconds -> print "UP",   exit code 0
#   anything else (no answer, an error status, slow) -> print "DOWN", exit code 1
# TODO (task health_check): your script here. The address is "$1".
