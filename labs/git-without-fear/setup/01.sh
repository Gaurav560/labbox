#!/usr/bin/env bash
# Chapter 1 setup: the shop repo with two commits, and a new file waiting to be committed.
set -euo pipefail
source /lab/setup/common.sh
cd /workspace
rm -rf shop
git init -q shop
cd shop
printf 'filter coffee 30\ncold coffee 40\nvada pav 25\n' > menu.txt
git add menu.txt && commit "2026-11-01T09:00:00+05:30" "Add the menu"
printf '# Brew Point shop\n\nThe menu and the shop notes.\n' > README.md
git add README.md && commit "2026-11-02T09:00:00+05:30" "Add a README"
printf 'Mon to Sat: 7:00 to 22:00\nSun: 8:00 to 20:00\n' > hours.txt
