#!/usr/bin/env bash
# Chapter 13 setup: last night's reports ran some slow commands, the slow log caught them, and then
# somebody switched the slow log off "to save CPU". The entries it caught are still there.
set -euo pipefail
R=(redis-cli)
limit=$("${R[@]}" CONFIG GET maxmemory | tail -1)
"${R[@]}" CONFIG SET maxmemory 0 > /dev/null  # seed even if chapter 14 is not fixed yet
"${R[@]}" SET lab:ch13:seen 1 > /dev/null
"${R[@]}" DEL report:2025 report:pages report:visitors > /dev/null
"${R[@]}" EVAL "for i = 1, 100000 do redis.call('ZADD', 'report:2025', i, 'order:' .. i) end return 1" 0 > /dev/null
"${R[@]}" EVAL "for i = 1, 60000 do redis.call('RPUSH', 'report:pages', 'page:' .. i) end return 1" 0 > /dev/null
"${R[@]}" EVAL "for i = 1, 60000 do redis.call('SADD', 'report:visitors', 'visitor:' .. i) end return 1" 0 > /dev/null
"${R[@]}" CONFIG SET maxmemory "$limit" > /dev/null
"${R[@]}" CONFIG SET slowlog-log-slower-than 1000 > /dev/null
"${R[@]}" SLOWLOG RESET > /dev/null
# The slowest runs first, so it is the oldest entry: the newest entry is not the slowest.
"${R[@]}" ZRANGE report:2025 0 -1 WITHSCORES > /dev/null
"${R[@]}" SMEMBERS report:visitors > /dev/null
"${R[@]}" LRANGE report:pages 0 -1 > /dev/null
"${R[@]}" UNLINK report:pages report:visitors > /dev/null
"${R[@]}" CONFIG SET slowlog-log-slower-than -1 > /dev/null
