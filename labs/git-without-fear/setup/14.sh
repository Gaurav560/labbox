#!/usr/bin/env bash
# Chapter 14 setup, the capstone: a messy repository. Pushed history, two local commits of which the first
# leaked a credentials file (the second "removed" it), and a finished feature branch waiting for a release.
set -euo pipefail
source /lab/setup/common.sh
fresh 14-capstone
git init -q --bare server/trails.git
git init -q trails && cd trails && trails_v1
git add README.md trails.md && commit "2026-11-22T09:00:00+05:30" "Add the README and two trails"
git remote add origin ../server/trails.git
git push -q -u origin main 2>/dev/null
git switch -q -c feature/maps
who Meera
printf '# Maps\n\nRajmachi: from Lonavala station, 15 km north.\n' > maps.md
git add maps.md && commit "2026-11-22T10:00:00+05:30" "Add a maps page"
git switch -q main
who Ravi
printf '{"maps_key": "not-a-real-key"}\n' > credentials.json
printf 'Start early. Carry water.\n' > tips.md
git add credentials.json tips.md && commit "2026-11-22T11:00:00+05:30" "Add trekking tips"
git rm -q credentials.json && commit "2026-11-22T11:05:00+05:30" "Remove credentials"
