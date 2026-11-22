#!/usr/bin/env bash
# Chapter 8: a slow report to run in the background, and a runaway program to practise stopping.
. /lab/setup/common.sh
fresh 08-processes
rm -f slow-report.sh hogger report.log report.pid
cat > slow-report.sh <<'SH'
#!/usr/bin/env bash
# Builds the night report. It is slow: it takes about 3 seconds.
echo "Report started"
sleep 3
echo "Last night: 41 captures, 2 lost to strong wind"
echo "Report done"
SH
cat > hogger <<'SH'
#!/bin/bash
# A runaway program: it uses a whole CPU core, doing nothing useful, until it is stopped.
# Run "./hogger stubborn" for a version that ignores the polite TERM signal.
[ "${1:-}" = stubborn ] && trap 'echo "hogger: I ignore TERM"' TERM
while :; do :; done
SH
chmod +x slow-report.sh hogger
