#!/usr/bin/env bash
# Chapter 3 setup: eight commits by three people, with two mistakes hidden in them.
set -euo pipefail
source /lab/setup/common.sh
fresh 03-history
git init -q trails && cd trails && trails_v1
git add README.md && commit "2026-11-03T09:00:00+05:30" "Add the README"
git add trails.md && commit "2026-11-03T10:00:00+05:30" "Add Rajmachi and Kalsubai"
who Ravi
cat >> trails.md <<'MD'

## Harishchandragad
- Distance: 14 km
- Difficulty: hard
- Best season: September to February
MD
git add trails.md && commit "2026-11-04T18:20:00+05:30" "Add Harishchandragad"
who Meera
sed -i 's/^- Best season: June to September$/- Best season: June to September\n- Water: Udhewadi village/' trails.md
git add trails.md && commit "2026-11-05T08:10:00+05:30" "Add a water point to Rajmachi"
who Ravi
sed -i 's/^- Best season: October to February$/- Best season: October to March/' trails.md
git add trails.md && commit "2026-11-06T21:05:00+05:30" "Fix Kalsubai's season"
who Asha
cat >> trails.md <<'MD'

## Lohagad
- Distance: 8 km
- Difficulty: easy
- Best season: June to October
MD
git add trails.md && commit "2026-11-07T07:40:00+05:30" "Add Lohagad"
who Meera
sed -i '/^- Water: Udhewadi village$/d' trails.md
git add trails.md && commit "2026-11-08T12:00:00+05:30" "Tidy up the Rajmachi section"
who Ravi
sed -i 's/^- Distance: 15 km$/- Distance: 51 km/' trails.md
git add trails.md && commit "2026-11-09T22:30:00+05:30" "Update Rajmachi's distance"
