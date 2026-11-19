#!/usr/bin/env bash
# Chapter 11 setup: someone "made Redis faster" by turning off all persistence.
set -euo pipefail
R=(redis-cli)
"${R[@]}" CONFIG SET appendonly no > /dev/null
"${R[@]}" CONFIG SET save "" > /dev/null
limit=$("${R[@]}" CONFIG GET maxmemory | tail -1)
"${R[@]}" CONFIG SET maxmemory 0 > /dev/null  # write the marker even if chapter 10 is not fixed yet
"${R[@]}" SET lab:ch11:since "$(date +%s)" > /dev/null
"${R[@]}" CONFIG SET maxmemory "$limit" > /dev/null
