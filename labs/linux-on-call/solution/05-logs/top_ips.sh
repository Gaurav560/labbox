#!/usr/bin/env bash
# top_ips.sh LOGFILE: print the 3 IP addresses with the most requests, busiest first, one per line.
awk '{print $2}' "$1" | sort | uniq -c | sort -rn | head -3 | awk '{print $2}'
