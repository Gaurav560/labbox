#!/usr/bin/env bash
# Chapter 7 setup: a pushed mistake (Kalsubai marked easy), and a commit lost by a hard reset.
set -euo pipefail
source /lab/setup/common.sh
fresh 07-undo-shared
git init -q --bare server/trails.git
git init -q trails && cd trails && trails_v1
git add README.md trails.md && commit "2026-11-14T09:00:00+05:30" "Add the README and two trails"
who Ravi
sed -i 's/^- Difficulty: hard$/- Difficulty: easy/' trails.md
git add trails.md && commit "2026-11-14T19:00:00+05:30" "Make Kalsubai easy"
who Meera
printf 'Start early. Carry water.\n' > tips.md
git add tips.md && commit "2026-11-15T08:00:00+05:30" "Add trekking tips"
git remote add origin ../server/trails.git
git push -q -u origin main 2>/dev/null
who Asha
cat >> trails.md <<'MD'

## Visapur
- Distance: 9 km
- Difficulty: moderate
- Best season: June to September
MD
git add trails.md && commit "2026-11-15T12:00:00+05:30" "Add Visapur"
git reset -q --hard HEAD~1
