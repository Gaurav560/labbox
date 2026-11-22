#!/usr/bin/env bash
# Chapter 16 setup: a second Redis server (service "replica") is running, but on its own.
set -euo pipefail
redis-cli -h replica REPLICAOF NO ONE > /dev/null
