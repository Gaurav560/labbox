#!/usr/bin/env bash
# Used only by `labbox test-lab`: every task, done the way the chapters teach it, after every setup has run.
set -euo pipefail
export HOME=/home/learner
q() { "$@" > /dev/null 2>&1; }

# 1. Why version control
cd /workspace/01-why-version-control/trails
git init -q
git add README.md trails.md
git commit -q -m "Add the README and the first two trails"

# 2. Commits
cd /workspace/02-commits/trails
git add rules.md && git commit -q -m "Add the safety rules"
git add trails.md && git commit -q -m "Add Harishchandragad"

# 3. History
cd /workspace/03-history
echo Ravi > answer-author.txt
git -C trails log -S "Water: Udhewadi" --format=%h -n 1 > answer-commit.txt

# 4. Branches
cd /workspace/04-branches/trails
git switch -q -c feature/monsoon
echo "Monsoon treks: carry a raincoat and check the forecast" > monsoon.md
git add monsoon.md && git commit -q -m "Add a monsoon page"
git switch -q main
git merge -q --no-edit feature/monsoon

# 5. Merge conflicts
cd /workspace/05-merge-conflicts/trails
q git merge ravi/rajmachi || true
sed -i '/^<<<<<<< /d; /^=======$/d; /^>>>>>>> /d; /^- Distance: 15.5 km$/d' trails.md
git add trails.md && git commit -q --no-edit
q git merge meera/readme || true
sed -i '/^<<<<<<< /d; /^=======$/d; /^>>>>>>> /d' README.md
git add README.md && git commit -q --no-edit

# 6. Undoing local work
cd /workspace/06-undo-local/trails
git restore trails.md
git rm -q --cached secrets.env
echo "secrets.env" >> .gitignore
git add .gitignore
git commit -q --amend --no-edit

# 7. Undoing shared history
cd /workspace/07-undo-shared/trails
git revert --no-edit "$(git log --format=%H --grep='Make Kalsubai easy' -n1)" > /dev/null
git push -q
git branch rescued "$(git reflog --format='%H %gs' | grep -m1 'commit: Add Visapur' | cut -d' ' -f1)"

# 8. Stash and clean
cd /workspace/08-stash/trails
git stash -q
git switch -q main
sed -i 's/Sahyadry/Sahyadri/' README.md
git add README.md && git commit -q -m "Fix the spelling of Sahyadri"
git switch -q feature/lohagad
git stash pop -q
git clean -q -f -d preview draft.tmp

# 9. Remotes
cd /workspace/09-remotes/trails
git pull -q
printf '\n## Visapur\n- Distance: 9 km\n- Difficulty: moderate\n' >> trails.md
git add trails.md && git commit -q -m "Add Visapur"
git push -q

# 10. A pull request
cd /workspace/10-pull-request/trails
git switch -q -c feature/torna
printf '\n## Torna\n- Distance: 7 km\n- Difficulty: moderate\n' >> trails.md
git add trails.md && git commit -q -m "Add Torna"
q git push -u origin feature/torna
echo "- Best season: October to February" >> trails.md
git add trails.md && git commit -q -m "Add Torna's best season, from the review"
q git push
git switch -q main
git merge -q --no-edit feature/torna
q git push

# 11. Rebase
cd /workspace/11-rebase/trails
q git rebase main
git reset -q --soft main
git commit -q -m "Add Sinhagad"

# 12. Inside git
cd /workspace/12-inside-git
git -C trails rev-parse 'HEAD^{tree}' > answer-tree.txt
git -C trails rev-parse HEAD:trails.md > answer-blob.txt

# 13. Good habits
cd /workspace/13-good-habits/trails
printf 'node_modules/\n*.log\n.env\n' > .gitignore
git add .gitignore && git commit -q -m "Ignore dependencies, logs and secrets"
git tag -a v1.0 -m "First release" "$(git log --format=%H --grep='Ready for the first release' -n1)"

# 14. Capstone
cd /workspace/14-capstone/trails
git reset -q --soft origin/main
git commit -q -m "Add trekking tips"
git merge -q --no-edit feature/maps
git tag -a v2.0 -m "Release 2.0: maps"
q git push origin main
q git push origin v2.0
