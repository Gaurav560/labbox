#!/usr/bin/env bash
# Chapter 13 setup: 30000 sessions, a huge analytics key, and a slow log that already shows trouble.
set -euo pipefail
R=(redis-cli)
limit=$("${R[@]}" CONFIG GET maxmemory | tail -1)
"${R[@]}" CONFIG SET maxmemory 0 > /dev/null  # seed even if chapter 10 is not fixed yet
"${R[@]}" SET lab:ch13:seen 1 > /dev/null
"${R[@]}" EVAL "for i = 1, 30000 do redis.call('SET', 'session:s' .. i, '{\"customer\": ' .. i .. '}') end return 1" 0 > /dev/null
"${R[@]}" DEL analytics:raw > /dev/null
"${R[@]}" EVAL "for i = 1, 150000 do redis.call('ZADD', 'analytics:raw', i, 'event:' .. i .. ':' .. string.rep('a', 20)) end return 1" 0 > /dev/null
"${R[@]}" CONFIG SET maxmemory "$limit" > /dev/null
"${R[@]}" CONFIG SET slowlog-log-slower-than 2000 > /dev/null
"${R[@]}" SLOWLOG RESET > /dev/null
"${R[@]}" ZRANGE analytics:raw 0 -1 > /dev/null   # the nightly report that freezes everyone
"${R[@]}" ZRANGE analytics:raw 0 -1 WITHSCORES > /dev/null
