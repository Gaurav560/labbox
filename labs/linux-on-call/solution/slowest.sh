#!/usr/bin/env bash
# slowest.sh LOGFILE: print the 3 slowest requests (the whole lines), slowest first.
sort -k6 -n -r "$1" | head -3
