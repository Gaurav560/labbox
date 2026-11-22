#!/usr/bin/env bash
# Chapter 5 setup: this month's customers at Basket's two dark stores.
set -euo pipefail
R=(redis-cli)
"${R[@]}" DEL customers:kothrud customers:baner > /dev/null
"${R[@]}" SADD customers:kothrud asha ravi meera kabir priya dev > /dev/null
"${R[@]}" SADD customers:baner ravi sana priya arjun dev zoya > /dev/null
