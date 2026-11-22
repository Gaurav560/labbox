#!/usr/bin/env bash
# Does, in the learner's workspace, every task that is done with commands rather than by writing a script.
set -euo pipefail
W=/workspace
cd $W/01-why-linux && echo pulsar > answer-hidden.txt && echo 'Crab Nebula' > answer-target.txt
cd $W/02-files/downloads && mkdir -p invoices photos && mv ./*.pdf invoices/ && mv ./*.jpg photos/ && rm ./*.tmp
cd $W/02-files && cp -r targets targets-backup
cd $W/03-reading-files && echo $(( $(wc -l < observations.csv) - 1 )) > answer-observations.txt && tail -n 20 app.log > recent.log
cd $W/04-pipes && { ./build.sh > /dev/null 2> errors.txt || true; } && sort -u targets.txt > tonight-targets.txt
cd $W/06-finding && find server -type f -size +1M > big-files.txt && grep -rl 'DB_PASSWORD=' server > answer-secret.txt
cd $W/07-permissions && chmod 755 hello.sh && chmod 600 keys/deploy-key.pem && chmod 700 keys
cd $W/09-disk-full && truncate -s 0 server/var/log/app/debug.log
cd $W/11-loops/photos && for f in IMG_*.JPG; do n=${f#IMG_}; mv "$f" "sky-${n%.JPG}.jpg"; done
chmod +x $W/12-environment/bin/tara-status
cd $W/13-networking && { python3 server.py 8080 > /dev/null 2>&1 & } && sleep 1 && curl -s localhost:8080/tonight > tonight-fetched.json
pkill -f 'server.py 8080' || true
cd $W/15-capstone/app && chmod +x start.sh && mkdir -p logs && chmod 644 tonight.json
