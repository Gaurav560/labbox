#!/usr/bin/env bash
# Used only by `labbox test-lab`: every redis-cli task the way the chapters teach, then the app.
set -euo pipefail
R=(redis-cli)
# Chapter 1
"${R[@]}" SET shop:name "Brew Point" > /dev/null
"${R[@]}" SET shop:city Pune > /dev/null
"${R[@]}" DEL cups:sold > /dev/null
for _ in 1 2 3; do "${R[@]}" INCR cups:sold > /dev/null; done
"${R[@]}" DECRBY beans:grams 250 > /dev/null
"${R[@]}" --scan --pattern 'tmp:import:*' | xargs -r "${R[@]}" DEL > /dev/null
# Chapter 2
"${R[@]}" SET otp:9876543210 4821 EX 300 > /dev/null
"${R[@]}" EXPIRE session:7f3a 1800 > /dev/null
"${R[@]}" PERSIST promo:diwali > /dev/null
# Chapter 3
"${R[@]}" DEL menu customer:42 orders:pending > /dev/null
"${R[@]}" HSET menu "filter coffee" 30 "cold coffee" 40 "vada pav" 25 > /dev/null
"${R[@]}" HSET customer:42 name Asha visits 7 > /dev/null
"${R[@]}" HINCRBY customer:42 visits 1 > /dev/null
"${R[@]}" HSET customer:42 tier gold > /dev/null
"${R[@]}" LPUSH orders:pending o1 o2 o3 > /dev/null
"${R[@]}" RPOP orders:pending > /dev/null
# Chapter 4
"${R[@]}" DEL visitors:today sales:today > /dev/null
"${R[@]}" SADD visitors:today asha ravi asha meera ravi > /dev/null
"${R[@]}" SINTERSTORE customers:both customers:andheri customers:bandra > /dev/null
"${R[@]}" ZADD sales:today 120 "filter coffee" 80 "vada pav" 45 "cold coffee" > /dev/null
"${R[@]}" ZINCRBY sales:today 5 "cold coffee" > /dev/null
# Chapter 5: the app in the background
cd /workspace
setsid nohup uvicorn app:app --host 0.0.0.0 --port 8000 > /tmp/app.log 2>&1 < /dev/null &
for _ in $(seq 1 50); do
  curl -s -o /dev/null localhost:8000/docs && exit 0
  sleep 0.2
done
cat /tmp/app.log
exit 1
