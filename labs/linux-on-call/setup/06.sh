#!/usr/bin/env bash
# Chapter 6: a server folder with many files, a few big ones, and one forgotten password.
. /lab/setup/common.sh
fresh 06-finding
rm -rf server big-files.txt answer-*.txt
mkdir -p server/app/handlers server/app/legacy server/config server/data server/logs/archive server/backups server/static/images
for f in targets dishes captures alerts; do printf 'def handle_%s(request):\n    return "ok"\n' "$f" > "server/app/handlers/$f.py"; done
printf 'from handlers import targets, dishes, captures, alerts\n' > server/app/main.py
printf '# Old settings from 2024, kept just in case.\nDB_HOST=10.0.0.5\nDB_USER=tara\nDB_PASSWORD=nebula-2024\n' > server/app/legacy/settings.old.conf
printf 'DB_HOST=db.internal\nDB_USER=tara\nDB_PASSWORD_FILE=/run/secrets/db\n' > server/config/database.env
printf 'PORT=8080\nAPP_ENV=production\n' > server/config/app.env
printf 'dish,diameter_m\ndish-1,12\ndish-2,12\ndish-3,9\n' > server/data/dishes.csv
for d in 19 20 21 22 23; do printf '2026-11-%s INFO night started\n' "$d" > "server/logs/app-2026-11-$d.log"; done
printf '<h1>Tara Observatory</h1>\n' > server/static/index.html
printf 'logo\n' > server/static/images/logo.svg
head -c 3145728 /dev/zero > server/backups/db-2026-11-22.sql.gz
head -c 2097152 /dev/zero > server/logs/archive/app-2026-10.log
head -c 1572864 /dev/zero > server/static/images/milky-way.jpg
head -c 921600 /dev/zero > server/data/cache.bin
