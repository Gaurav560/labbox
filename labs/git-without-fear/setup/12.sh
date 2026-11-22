#!/usr/bin/env bash
# Chapter 12 setup: a small repository to look inside.
set -euo pipefail
source /lab/setup/common.sh
fresh 12-inside-git
git init -q trails && cd trails && trails_v1
git add README.md && commit "2026-11-20T09:00:00+05:30" "Add the README"
git add trails.md && commit "2026-11-20T09:30:00+05:30" "Add Rajmachi and Kalsubai"
