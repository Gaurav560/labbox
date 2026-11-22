#!/usr/bin/env bash
# Chapter 9 setup: a "server" repository, your clone of it, and a commit Ravi pushed after you cloned.
set -euo pipefail
source /lab/setup/common.sh
fresh 09-remotes
git init -q trails-start && cd trails-start && trails_v1
git add README.md trails.md && commit "2026-11-17T09:00:00+05:30" "Add the README and two trails"
cd .. && git clone -q --bare trails-start server/trails.git && rm -rf trails-start
git clone -q server/trails.git trails
# Ravi pushes from his own copy.
git clone -q server/trails.git /tmp/ravi && cd /tmp/ravi
who Ravi
printf '\n## Harishchandragad\n- Distance: 14 km\n- Difficulty: hard\n' >> trails.md
git add trails.md && commit "2026-11-17T20:00:00+05:30" "Add Harishchandragad"
git push -q origin main 2>/dev/null
cd / && rm -rf /tmp/ravi
