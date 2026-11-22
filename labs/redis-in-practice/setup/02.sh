#!/usr/bin/env bash
# Chapter 2 setup: the egg stock, and leftovers from an old import script to clean up.
set -euo pipefail
R=(redis-cli)
"${R[@]}" SET stock:eggs 120 > /dev/null
for i in 1 2 3 4 5; do "${R[@]}" SET "tmp:import:$i" "row $i" > /dev/null; done
