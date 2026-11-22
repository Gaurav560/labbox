#!/usr/bin/env bash
# Chapter 15 (capstone): the status app is down on the night of an eclipse. Three things are wrong; the learner finds them.
. /lab/setup/common.sh
fresh 15-capstone
rm -rf app
mkdir -p app
cd app
write_server
sed -i 's/int(os.environ.get("PORT", "8080"))/int(os.environ["PORT"])/' server.py
printf '# Settings for the Tara observatory app.\nPORT=8090\nAPP_ENV=production\n' > app.env
cat > start.sh <<'SH'
#!/usr/bin/env bash
# start.sh: start the Tara observatory app in the background.
# Its output goes to logs/app.log and its process id to app.pid.
cd "$(dirname "$0")"
set -a; . ./app.env; set +a
nohup python3 server.py >> logs/app.log 2>&1 &
echo $! > app.pid
echo "Tara app started (PID $(cat app.pid)) on port $PORT"
SH
chmod 644 start.sh
chmod 000 tonight.json
