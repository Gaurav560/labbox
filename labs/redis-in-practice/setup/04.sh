#!/usr/bin/env bash
# Chapter 4 setup: this month's customers at two outlets.
set -euo pipefail
R=(redis-cli)
"${R[@]}" DEL customers:andheri customers:bandra > /dev/null
"${R[@]}" SADD customers:andheri asha ravi meera kabir priya dev > /dev/null
"${R[@]}" SADD customers:bandra ravi sana priya arjun dev zoya > /dev/null
