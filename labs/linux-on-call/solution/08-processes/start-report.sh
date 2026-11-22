#!/usr/bin/env bash
# start-report.sh: start ./slow-report.sh in the background and come back at once.
#   - it must keep running even if you close the terminal
#   - everything it prints goes into report.log
#   - its process id goes into report.pid
nohup ./slow-report.sh > report.log 2>&1 &
echo $! > report.pid
