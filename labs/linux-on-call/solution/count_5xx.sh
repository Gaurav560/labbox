#!/usr/bin/env bash
# count_5xx.sh LOGFILE: print how many requests failed with a 5xx status (500 to 599). Just the number.
awk '$5 >= 500 && $5 <= 599' "$1" | wc -l
