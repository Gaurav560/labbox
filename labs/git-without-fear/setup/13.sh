#!/usr/bin/env bash
# Chapter 13 setup: files that must never be committed, and a commit ready to release.
set -euo pipefail
source /lab/setup/common.sh
fresh 13-good-habits
git init -q trails && cd trails && trails_v1
git add README.md trails.md && commit "2026-11-21T09:00:00+05:30" "Add the README and two trails"
printf 'Start early. Carry water.\n' > tips.md
git add tips.md && commit "2026-11-21T10:00:00+05:30" "Ready for the first release"
mkdir -p node_modules/marked && printf 'module.exports = {}\n' > node_modules/marked/index.js
printf 'build started\nbuild done\n' > build.log
printf 'MAPS_API_KEY=not-a-real-key\n' > .env
