#!/usr/bin/env bash
# Chapter 11 setup: main moved on while feature/sinhagad grew three small commits.
set -euo pipefail
source /lab/setup/common.sh
fresh 11-rebase
git init -q trails && cd trails && trails_v1
git add README.md trails.md && commit "2026-11-19T09:00:00+05:30" "Add the README and two trails"
git switch -q -c feature/sinhagad
who Meera
printf '\n## Sinhagad\n' >> trails.md
git add trails.md && commit "2026-11-19T10:00:00+05:30" "wip"
printf -- '- Distance: 6 km\n- Difficulty: moderate\n' >> trails.md
git add trails.md && commit "2026-11-19T10:10:00+05:30" "wip again"
printf -- '- Best season: all year\n' >> trails.md
git add trails.md && commit "2026-11-19T10:20:00+05:30" "done Sinhagad"
git switch -q main
who Asha
printf 'Start early. Carry water.\n' > tips.md
git add tips.md && commit "2026-11-19T11:00:00+05:30" "Add trekking tips"
sed -i 's/Sahyadri hills/Sahyadri hills of Maharashtra/' README.md
git add README.md && commit "2026-11-19T11:30:00+05:30" "Say where the Sahyadri are"
git switch -q feature/sinhagad
