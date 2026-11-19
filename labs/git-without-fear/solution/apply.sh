#!/usr/bin/env bash
# Used only by `labbox test-lab`: every task, done the way the chapters teach.
set -euo pipefail
export HOME=/home/learner
cd /workspace/shop
git add hours.txt
git commit -q -m "Add opening hours"
git switch -q -c feature/combo
echo "filter coffee + vada pav = 50" > combo.txt
git add combo.txt
git commit -q -m "Add the breakfast combo"
git switch -q main
git merge -q --no-edit feature/combo

cd /workspace/kitchen
git rm -q --cached secrets.env
echo "secrets.env" >> .gitignore
git add .gitignore
git commit -q --amend --no-edit
git revert --no-edit "$(git log --format=%H --grep='Raise filter coffee' -n1)" > /dev/null
