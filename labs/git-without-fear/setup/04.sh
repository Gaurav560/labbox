#!/usr/bin/env bash
# Chapter 4 setup: a repository on main, ready for a feature branch.
set -euo pipefail
source /lab/setup/common.sh
fresh 04-branches
git init -q trails && cd trails && trails_v1
git add README.md && commit "2026-11-10T09:00:00+05:30" "Add the README"
git add trails.md && commit "2026-11-10T09:30:00+05:30" "Add Rajmachi and Kalsubai"
