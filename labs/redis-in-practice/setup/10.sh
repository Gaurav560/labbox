#!/usr/bin/env bash
# Chapter 10 setup: the incident. A forgotten debug log grew huge, the cache filled the rest, and
# Redis (maxmemory 64 MB, policy noeviction) now refuses every write with an OOM error.
set -euo pipefail
R=(redis-cli)
"${R[@]}" CONFIG SET maxmemory-policy noeviction > /dev/null
"${R[@]}" SET lab:ch10:seen 1 > /dev/null
# Redis checks maxmemory when a script starts, not inside it, so both fills go in batches.
for start in $(seq 1 2000 260000); do
  "${R[@]}" EVAL "for i = tonumber(ARGV[1]), tonumber(ARGV[1]) + 1999 do redis.call('RPUSH', 'debug:log', 'request ' .. i .. ' ' .. string.rep('x', 80)) end return 1" 0 "$start" > /dev/null
done
# Cache entries (each with a TTL, as cache entries should have) until Redis is full.
for batch in $(seq 0 150); do
  out=$("${R[@]}" EVAL "for i = 1, 1000 do redis.call('SET', 'cache:page:' .. (ARGV[1] * 1000 + i), string.rep('c', 1000), 'EX', 7200) end return 1" 0 "$batch" 2>&1)
  case "$out" in *OOM*) break ;; esac
done
