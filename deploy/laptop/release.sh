#!/usr/bin/env bash
# Put one commit live (deploy/laptop/README.md): build it in its own folder, migrate, switch, check, and switch
# back if the check fails. The deploy timer runs it when the production branch moves; `prod deploy` by hand.
#
#   deploy/laptop/release.sh <commit>
set -euo pipefail

PROD=/srv/labbox/prod
SRC="$PROD/src"
LOG="$PROD/deploy.log"
HEALTH_URL=http://127.0.0.1:8100/api/health
PAGE_URL=http://127.0.0.1:8180/
KEEP=3  # releases kept on disk (the live one and the one before it are never removed)
SERVICES=(labbox-prod.service labbox-prod-worker.service labbox-prod-caddy.service)

[ $# -eq 1 ] || { echo "Usage: $0 <commit>" >&2; exit 2; }
exec 9>"$PROD/deploy.lock"
flock -n 9 || { echo "Another deploy is running." >&2; exit 1; }
exec > >(while IFS= read -r line; do printf '%s %s\n' "$(date '+%F %T')" "$line"; done | tee -a "$LOG") 2>&1

say() { printf '==> %s\n' "$*"; }
live_env() { set -a; . "$PROD/shared/.env"; set +a; }
release_of() { basename "$(readlink -f "$1" 2>/dev/null)" 2>/dev/null || true; }

git -C "$SRC" fetch -q origin
SHA="$(git -C "$SRC" rev-parse --verify "$1^{commit}")"
DIR="$PROD/releases/$SHA"
PREV="$(release_of "$PROD/current")"
[ -d "$PROD/releases/$PREV" ] || PREV=""

if [ "$SHA" = "$PREV" ]; then
  say "${SHA:0:12} is already live."
  exit 0
fi
say "Release ${SHA:0:12} ($(git -C "$SRC" log -1 --format=%s "$SHA")); live now: ${PREV:0:12}"
# Older commits name lab machines like development's (lab-u1-...): live and development would stop each
# other's machines. Only commits that know INSTANCE may go live.
if ! git -C "$SRC" show "$SHA:backend/app/config.py" | grep -q '^    INSTANCE: str'; then
  say "REFUSED: ${SHA:0:12} predates the INSTANCE setting (27 November); deploy a newer commit."
  exit 1
fi

build() {
  if [ -f "$DIR/.built" ]; then
    say "Already built"
    return
  fi
  [ -d "$DIR" ] || git -C "$SRC" worktree add -q --detach "$DIR" "$SHA"
  say "Backend packages"
  [ -x "$DIR/backend/.venv/bin/python" ] || /usr/bin/python3.12 -m venv "$DIR/backend/.venv"
  "$DIR/backend/.venv/bin/pip" install -q --disable-pip-version-check -r "$DIR/backend/requirements.txt"
  ln -sfn "$PROD/shared/.env" "$DIR/backend/.env"
  say "Frontend build"
  (cd "$DIR/frontend" && npm ci --no-audit --no-fund --loglevel=error && npm run build --silent)
  say "Labs meet the standard"
  (live_env && cd "$DIR" && scripts/labbox validate --strict >/dev/null)
  touch "$DIR/.built"
}

images() {
  [ -n "$PREV" ] || { say "First release: lab images as built on this machine"; return; }
  local changed
  changed="$(git -C "$SRC" diff --name-only "$PREV" "$SHA" -- images labs)"
  if grep -q '^images/' <<<"$changed"; then
    say "Base images changed: building every image"
    "$DIR/scripts/build_lab_images.sh"
    return
  fi
  local lab image
  for lab in $(grep '^labs/' <<<"$changed" | cut -d/ -f2 | sort -u); do
    [ -f "$DIR/labs/$lab/Dockerfile" ] || continue
    image="$(grep -E '^image:' "$DIR/labs/$lab/lab.yaml" | awk '{print $2}')"
    say "Image $image"
    docker build -q -t "$image" "$DIR/labs/$lab" >/dev/null
  done
}

migrate() {
  say "Database migrations (additive only)"
  (live_env && cd "$DIR/backend" && .venv/bin/python -c 'from app.db import init_db; init_db()')
}

switch_to() { # release folder name
  ln -sfn "$PROD/releases/$1" "$PROD/current.new"
  mv -Tf "$PROD/current.new" "$PROD/current"
  (umask 077; echo "RELEASE=$1" > "$PROD/shared/release.env")
  systemctl --user enable -q "${SERVICES[@]}"
  systemctl --user restart "${SERVICES[@]}"
}

healthy() { # commit; up to about three minutes
  local want="$1" i
  for i in $(seq 90); do
    if curl -fsS -m 5 "$HEALTH_URL" 2>/dev/null | python3 -c "
import json, sys
h = json.load(sys.stdin)
sys.exit(0 if h.get('release') == '$want' and h.get('docker') and h.get('database') and h.get('shared_state') else 1)
" 2>/dev/null && curl -fsS -m 5 "$PAGE_URL" 2>/dev/null | grep -q 'id="root"'; then
      return 0
    fi
    sleep 2
  done
  return 1
}

prune() {
  local keep=0 d name
  for d in $(ls -1td "$PROD"/releases/*/ 2>/dev/null); do
    name="$(basename "$d")"
    if [ "$name" = "$SHA" ] || [ "$name" = "$PREV" ]; then
      continue
    fi
    keep=$((keep + 1))
    if [ "$keep" -gt $((KEEP - 2)) ]; then
      git -C "$SRC" worktree remove --force "$d" 2>/dev/null || rm -rf "$d"
    fi
  done
  git -C "$SRC" worktree prune
}

# Steps run at the top level so `set -e` stops at the first error (it is off inside `step || ...`); the exit
# trap then marks the commit as failed. Nothing has changed for learners until the switch.
STEP=""
on_exit() {
  local rc=$?
  if [ "$rc" -ne 0 ] && [ -n "$STEP" ]; then
    echo "$SHA" > "$PROD/failed"
    say "FAILED during $STEP; the live site is unchanged (${PREV:0:12})"
  fi
}
trap on_exit EXIT

STEP=build; build
STEP="lab images"; images
STEP=migrations; migrate
STEP=""
say "Switching to ${SHA:0:12}"
switch_to "$SHA"
if healthy "$SHA"; then
  echo "$SHA" > "$PROD/last-good"
  [ -n "$PREV" ] && echo "$PREV" > "$PROD/previous"
  # A rollback keeps its hold on the newer commit (prod rollback wrote it to failed).
  if [ "$(cat "$PROD/failed" 2>/dev/null)" = "$SHA" ]; then rm -f "$PROD/failed"; fi
  prune
  say "LIVE: ${SHA:0:12}"
  exit 0
fi
say "Health check failed: journalctl --user -u labbox-prod -n 100"
echo "$SHA" > "$PROD/failed"
if [ -n "$PREV" ]; then
  say "Switching back to ${PREV:0:12}"
  switch_to "$PREV"
  healthy "$PREV" && say "Back on ${PREV:0:12}" || say "The previous release is not healthy either"
fi
exit 1
