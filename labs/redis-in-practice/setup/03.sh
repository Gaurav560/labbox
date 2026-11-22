#!/usr/bin/env bash
# Chapter 3 setup: a login session that never expires (a bug), and a promo that is about to.
set -euo pipefail
R=(redis-cli)
"${R[@]}" SET session:7f3a '{"customer": 42, "store": "kothrud"}' > /dev/null
"${R[@]}" SET promo:diwali "20% off mangoes" EX 3600 > /dev/null
