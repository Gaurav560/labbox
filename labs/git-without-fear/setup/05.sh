#!/usr/bin/env bash
# Chapter 5 setup: two branches that changed the same lines as main: two merges, two conflicts.
set -euo pipefail
source /lab/setup/common.sh
fresh 05-merge-conflicts
git init -q trails && cd trails && trails_v1
git add README.md trails.md && commit "2026-11-11T09:00:00+05:30" "Add the README and two trails"
# Ravi re-measured Rajmachi with GPS, on his branch.
git switch -q -c ravi/rajmachi
who Ravi
sed -i 's/^- Distance: 15 km$/- Distance: 16 km/' trails.md
git add trails.md && commit "2026-11-11T18:00:00+05:30" "Rajmachi is 16 km by GPS"
# Meera adds a photo credit line to the README, on her branch.
git switch -q main
git switch -q -c meera/readme
who Meera
printf '\nPhotos by Meera.\n' >> README.md
git add README.md && commit "2026-11-12T10:00:00+05:30" "Credit the photos"
# Meanwhile on main, Asha changed the same two places.
git switch -q main
who Asha
sed -i 's/^- Distance: 15 km$/- Distance: 15.5 km/' trails.md
git add trails.md && commit "2026-11-12T11:00:00+05:30" "Rajmachi is 15.5 km from the map"
printf '\nMaps by Asha.\n' >> README.md
git add README.md && commit "2026-11-12T12:00:00+05:30" "Credit the maps"
