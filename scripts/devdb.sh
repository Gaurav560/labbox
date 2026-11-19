#!/usr/bin/env bash
# LabBox's own Postgres 16 and Redis 7 for development: two Docker containers on localhost only, on
# their own ports (55432 and 56379) so they never clash with a Postgres or Redis already on the machine.
# Data lives in Docker volumes and survives restarts. Safe to run again; it skips what is there.
#
#   scripts/devdb.sh          start both (creates them the first time)
#   scripts/devdb.sh url      print the DATABASE_URL and REDIS_URL lines for backend/.env
#   scripts/devdb.sh status   show whether they run
#   scripts/devdb.sh stop     stop both (data stays)
#
# The Postgres password is made once at random and kept in $SECRET (only your user can read it).
set -euo pipefail
PG=labbox-postgres
RD=labbox-redis
PG_PORT=55432
RD_PORT=56379
SECRET="${LABBOX_DEVDB_SECRET:-/srv/labbox/devdb.password}"

password() {
  if [ ! -s "$SECRET" ]; then
    mkdir -p "$(dirname "$SECRET")"
    (umask 077; head -c 24 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' > "$SECRET")
  fi
  cat "$SECRET"
}

up() { # name, docker run args...
  local name=$1; shift
  if ! docker ps -a --format '{{.Names}}' | grep -qx "$name"; then
    docker run -d --name "$name" --restart unless-stopped "$@" >/dev/null
    echo "created $name"
  elif [ "$(docker inspect -f '{{.State.Running}}' "$name")" != "true" ]; then
    docker start "$name" >/dev/null && echo "started $name"
  else
    echo "$name already running"
  fi
}

case "${1:-start}" in
  start)
    PW=$(password)
    up "$PG" -p 127.0.0.1:$PG_PORT:5432 -v labbox-postgres:/var/lib/postgresql/data \
      -e POSTGRES_USER=labbox -e POSTGRES_PASSWORD="$PW" -e POSTGRES_DB=labbox postgres:16
    up "$RD" -p 127.0.0.1:$RD_PORT:6379 -v labbox-redis:/data redis:7.4 redis-server --appendonly yes
    for _ in $(seq 1 60); do docker exec "$PG" pg_isready -U labbox -q && break; sleep 1; done
    docker exec "$PG" pg_isready -U labbox
    docker exec "$RD" redis-cli ping
    echo "Next: scripts/devdb.sh url  (the lines for backend/.env)"
    ;;
  url)
    echo "DATABASE_URL=postgresql+psycopg://labbox:$(password)@127.0.0.1:$PG_PORT/labbox"
    echo "REDIS_URL=redis://127.0.0.1:$RD_PORT/0"
    ;;
  status)
    docker ps -a --filter "name=^($PG|$RD)$" --format '{{.Names}}: {{.Status}}'
    ;;
  stop)
    docker stop "$PG" "$RD" >/dev/null && echo "stopped (data kept in the Docker volumes)"
    ;;
  *)
    echo "usage: scripts/devdb.sh [start|url|status|stop]" >&2; exit 2
    ;;
esac
