#!/usr/bin/env bash
# Chapter 1 setup: the coffee bean stock, and leftovers from an old import script to clean up.
set -euo pipefail
R=(redis-cli)
"${R[@]}" SET beans:grams 1000 > /dev/null
for i in 1 2 3 4 5; do "${R[@]}" SET "tmp:import:$i" "row $i" > /dev/null; done
