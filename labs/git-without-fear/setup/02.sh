#!/usr/bin/env bash
# Chapter 2 setup: a repository with two commits, a new file to commit, and two changed files of which only one
# belongs in the next commit.
set -euo pipefail
source /lab/setup/common.sh
fresh 02-commits
git init -q trails && cd trails && trails_v1
printf 'Ideas for later:\n- a map page\n' > notes.txt
git add README.md notes.txt && commit "2026-11-02T09:00:00+05:30" "Add the README and a notes file"
git add trails.md && commit "2026-11-02T09:30:00+05:30" "Add Rajmachi and Kalsubai"
cat > rules.md <<'MD'
# Safety rules

1. Tell someone where you are going.
2. Carry two litres of water.
3. Start back before 3 pm.
MD
cat >> trails.md <<'MD'

## Harishchandragad
- Distance: 14 km
- Difficulty: hard
- Best season: September to February
MD
printf -- '- ask Ravi about the night trek\n' >> notes.txt
