#!/usr/bin/env bash
# Chapter 8 setup: half-written work on a feature branch when an urgent fix is needed on main; and junk files.
set -euo pipefail
source /lab/setup/common.sh
fresh 08-stash
git init -q trails && cd trails && trails_v1
sed -i 's/Sahyadri/Sahyadry/' README.md
git add README.md trails.md && commit "2026-11-16T09:00:00+05:30" "Add the README and two trails"
git switch -q -c feature/lohagad
printf '\n## Lohagad\n- Distance: 8 km\n' >> trails.md
mkdir -p preview && printf '<html>draft</html>\n' > preview/index.html
printf 'scratch\n' > draft.tmp
printf '# Ideas\n- a page for monsoon treks\n' > ideas.md
