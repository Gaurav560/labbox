#!/usr/bin/env bash
# Chapter 9 setup: a payments stream whose worker crashed with two payments still unacknowledged.
set -euo pipefail
R=(redis-cli)
"${R[@]}" DEL payments:stream > /dev/null
"${R[@]}" XADD payments:stream '*' order o101 amount 120 > /dev/null
"${R[@]}" XADD payments:stream '*' order o102 amount 45 > /dev/null
"${R[@]}" XGROUP CREATE payments:stream billing 0 > /dev/null
# worker-crashed reads both, then dies: they stay pending, owned by it. IDLE makes them look 10 minutes old.
"${R[@]}" XREADGROUP GROUP billing worker-crashed COUNT 2 STREAMS payments:stream '>' > /dev/null
for id in $("${R[@]}" XRANGE payments:stream - + | grep -E '^[0-9]+-[0-9]+$'); do
  "${R[@]}" XCLAIM payments:stream billing worker-crashed 0 "$id" IDLE 600000 > /dev/null
done
