#!/usr/bin/env bash
# Chapter 6 setup: the last commit (not pushed anywhere) added a secrets file by mistake, and trails.md has
# been half deleted by accident in the working folder, next to good, unsaved edits in notes.md.
set -euo pipefail
source /lab/setup/common.sh
fresh 06-undo-local
git init -q trails && cd trails && trails_v1
printf '# Notes\n' > notes.md
git add README.md trails.md notes.md && commit "2026-11-13T09:00:00+05:30" "Add the README, trails and notes"
printf '\nAsk Asha for the maps API settings.\n' >> README.md
printf 'MAPS_API_KEY=not-a-real-key\n' > secrets.env
git add README.md secrets.env && commit "2026-11-13T10:00:00+05:30" "Add the maps settings"
# The accident: most of trails.md deleted. And good work, not committed yet.
head -n 4 trails.md > /tmp/t && mv /tmp/t trails.md
printf -- '- try the Rajmachi night trek in December\n' >> notes.md
