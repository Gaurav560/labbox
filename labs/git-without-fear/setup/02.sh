#!/usr/bin/env bash
# Chapter 2 setup: the kitchen repo. A typo commit that is already pushed, then an unpushed commit
# that adds a secrets file by mistake.
set -euo pipefail
source /lab/setup/common.sh
cd /workspace
rm -rf kitchen kitchen-origin.git
git init -q --bare kitchen-origin.git
git init -q kitchen
cd kitchen
printf 'filter coffee 30\ncold coffee 40\n' > menu.txt
git add menu.txt && commit "2026-11-03T09:00:00+05:30" "Add the kitchen menu"
sed -i 's/^filter coffee 30$/filter coffee 300/' menu.txt
git add menu.txt && commit "2026-11-04T09:00:00+05:30" "Raise filter coffee to 300"
printf 'Grind the beans at 6:30\nBoil milk at 6:45\n' > prep.txt
git add prep.txt && commit "2026-11-05T09:00:00+05:30" "Add the prep list"
git remote add origin ../kitchen-origin.git
git push -q -u origin main
printf '# Kitchen\n\nOpens at 7. Ask Kabir for the SMS settings.\n' > README.md
printf 'SMS_API_KEY=not-a-real-key\n' > secrets.env
git add README.md secrets.env && commit "2026-11-06T09:00:00+05:30" "Add a README and the SMS settings"
