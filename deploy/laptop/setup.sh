#!/usr/bin/env bash
# One-time setup of the live site on this laptop (see deploy/laptop/README.md). Safe to run again: it skips
# what is there and never overwrites the live .env. No sudo.
#
#   deploy/laptop/setup.sh [--copy-openai-key]   folders, Caddy and cloudflared, database, .env, services
#   deploy/laptop/setup.sh tunnel <hostname>     Cloudflare login (a link to open), the tunnel, its DNS record
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DEV="$(cd "$HERE/../.." && pwd)"
PROD=/srv/labbox/prod
BIN="$HOME/.local/bin"
UNITS="$HOME/.config/systemd/user"
REPO_URL="${LABBOX_REPO_URL:-https://github.com/Gaurav560/labbox.git}"
PG=labbox-postgres
PG_PORT=55432
RD_PORT=56379
HOSTNAME_FILE="$PROD/shared/hostname"

# Pinned tools (checked 27 November 2026; each at least two weeks old). sha256 from the GitHub release.
CADDY_VERSION=2.11.9
CADDY_SHA256=5b8cb7faf8726a2028ad96a66e54e6e81e8f361bc6175e5d22bbd997cc5177fb
CLOUDFLARED_VERSION=2026.10.7
CLOUDFLARED_SHA256=1f99fb518b83dec2ba8d870a7cc991d82a77e6196295a3d2754ba17ab9f91872

say() { printf '==> %s\n' "$*"; }

fetch() { # url, sha256, target
  local tmp
  tmp="$(mktemp)"
  curl -fsSL "$1" -o "$tmp"
  if ! echo "$2  $tmp" | sha256sum -c --status; then
    rm -f "$tmp"
    echo "Checksum mismatch for $1" >&2
    exit 1
  fi
  mv "$tmp" "$3"
}

tools() {
  mkdir -p "$BIN"
  if ! "$BIN/caddy" version 2>/dev/null | grep -q "v$CADDY_VERSION"; then
    say "Caddy $CADDY_VERSION"
    local tgz dir
    dir="$(mktemp -d)"
    tgz="$dir/caddy.tar.gz"
    fetch "https://github.com/caddyserver/caddy/releases/download/v$CADDY_VERSION/caddy_${CADDY_VERSION}_linux_amd64.tar.gz" \
      "$CADDY_SHA256" "$tgz"
    tar -xzf "$tgz" -C "$dir" caddy
    install -m 0755 "$dir/caddy" "$BIN/caddy"
    rm -rf "$dir"
  fi
  if ! "$BIN/cloudflared" --version 2>/dev/null | grep -q "$CLOUDFLARED_VERSION"; then
    say "cloudflared $CLOUDFLARED_VERSION"
    fetch "https://github.com/cloudflare/cloudflared/releases/download/$CLOUDFLARED_VERSION/cloudflared-linux-amd64" \
      "$CLOUDFLARED_SHA256" "$BIN/cloudflared"
    chmod 0755 "$BIN/cloudflared"
  fi
}

folders() {
  say "Folders in $PROD"
  mkdir -p "$PROD"/{releases,shared,volumes,checks,library}
  mkdir -p -m 0700 "$PROD/backups"
  chmod 0700 "$PROD/shared"
  if [ ! -d "$PROD/src/.git" ]; then
    git clone -q "$REPO_URL" "$PROD/src"
  fi
}

random() { head -c 48 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c "$1"; }

database() { # prints the live database password (made once, kept in shared/db.password)
  local pw_file="$PROD/shared/db.password"
  if [ ! -s "$pw_file" ]; then
    (umask 077; random 32 > "$pw_file")
  fi
  local pw
  pw="$(cat "$pw_file")"
  if ! docker exec "$PG" psql -U labbox -d postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='labbox_prod'" | grep -q 1; then
    say "Database role labbox_prod"
    docker exec -i "$PG" psql -q -U labbox -d postgres -v ON_ERROR_STOP=1 -v pw="$pw" >/dev/null <<'SQL'
CREATE ROLE labbox_prod LOGIN PASSWORD :'pw';
SQL
  fi
  if ! docker exec "$PG" psql -U labbox -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='labbox_prod'" | grep -q 1; then
    say "Database labbox_prod"
    docker exec "$PG" psql -q -U labbox -d postgres -c "CREATE DATABASE labbox_prod OWNER labbox_prod"
  fi
}

env_file() {
  local env="$PROD/shared/.env" host
  host="$(cat "$HOSTNAME_FILE" 2>/dev/null || echo labbox.gauravships.systems)"
  if [ ! -s "$env" ]; then
    say "Live settings in $env (new secrets; never printed)"
    (umask 077; cat > "$env" <<EOF
# The live site's settings (deploy/laptop/setup.sh). Development uses backend/.env, never this file.
INSTANCE=prod
JWT_SECRET=$(random 48)
DATABASE_URL=postgresql+psycopg://labbox_prod:$(cat "$PROD/shared/db.password")@127.0.0.1:$PG_PORT/labbox_prod
# Redis database 2: development uses 0, tests 15.
REDIS_URL=redis://127.0.0.1:$RD_PORT/2
VOLUMES_DIR=$PROD/volumes
CHECKS_DIR=$PROD/checks
BACKUP_DIR=$PROD/backups
LIBRARY_UPLOADS_DIR=$PROD/library
CORS_ORIGINS=https://$host
# Invite only: learners' code runs on this laptop. Accounts: deploy/laptop/prod adduser <name>
ALLOW_SIGNUP=false
LLM_GATEWAY_PORT=9100
SENTRY_ENVIRONMENT=production
EOF
    )
  fi
  if [ "${COPY_KEY:-0}" = 1 ] && ! grep -q '^OPENAI_API_KEY=.' "$env"; then
    if grep -q '^OPENAI_API_KEY=.' "$DEV/backend/.env" 2>/dev/null; then
      { echo "# Copied from backend/.env by setup.sh --copy-openai-key"; grep '^OPENAI_API_KEY=' "$DEV/backend/.env"; } >> "$env"
      say "OpenAI key copied (not shown)"
    fi
  fi
  if ! grep -q '^OPENAI_API_KEY=.' "$env"; then
    echo "    Note: no OPENAI_API_KEY in $env yet; the tutor and AI labs stay off until it is added."
  fi
}

services() {
  say "Services (systemd --user)"
  mkdir -p "$UNITS"
  for unit in "$HERE"/systemd/*; do
    install -m 0644 "$unit" "$UNITS/$(basename "$unit")"
  done
  systemctl --user daemon-reload
  # The app's services start with the first release (release.sh enables them); the timer starts now.
  if [ -e "$PROD/current" ]; then
    systemctl --user enable labbox-prod.service labbox-prod-worker.service labbox-prod-caddy.service >/dev/null
  fi
  systemctl --user enable --now labbox-prod-deploy.timer >/dev/null
  if [ -f "$HOME/.cloudflared/labbox.yml" ]; then
    systemctl --user enable --now labbox-prod-tunnel.service >/dev/null
  fi
  if [ "$(loginctl show-user "$USER" -p Linger --value 2>/dev/null)" != yes ]; then
    echo "    Note: run once:  sudo loginctl enable-linger $USER   (the site then runs after a reboot without a login)"
  fi
}

tunnel() { # hostname
  local host="$1" cf="$BIN/cloudflared" cfg="$HOME/.cloudflared/labbox.yml"
  [ -n "$host" ] || { echo "Usage: $0 tunnel <hostname>" >&2; exit 2; }
  echo "$host" > "$HOSTNAME_FILE"
  if [ ! -f "$HOME/.cloudflared/cert.pem" ]; then
    say "Cloudflare login: open the link below, pick the domain, click Authorize"
    "$cf" tunnel login
  fi
  if ! "$cf" tunnel info labbox >/dev/null 2>&1; then
    say "Tunnel labbox"
    "$cf" tunnel create labbox
  fi
  local id
  id="$("$cf" tunnel info --output json labbox | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')"
  say "DNS: $host -> tunnel $id"
  "$cf" tunnel route dns --overwrite-dns labbox "$host"
  cat > "$cfg" <<EOF
# The live site's tunnel (deploy/laptop/setup.sh tunnel). Everything goes to Caddy, which serves the app.
tunnel: $id
credentials-file: $HOME/.cloudflared/$id.json
ingress:
  - hostname: $host
    service: http://127.0.0.1:8180
  - service: http_status:404
EOF
  if grep -q '^CORS_ORIGINS=' "$PROD/shared/.env" 2>/dev/null; then
    sed -i "s#^CORS_ORIGINS=.*#CORS_ORIGINS=https://$host#" "$PROD/shared/.env"
  fi
  systemctl --user enable labbox-prod-tunnel.service >/dev/null
  systemctl --user restart labbox-prod-tunnel.service
  say "Tunnel running: https://$host"
}

case "${1:-}" in
  tunnel) tools; tunnel "${2:-}" ;;
  ""|--copy-openai-key)
    [ "${1:-}" = --copy-openai-key ] && COPY_KEY=1
    tools; folders; database; env_file; services
    say "Done. First release: deploy/laptop/prod deploy <commit> (or the GitHub Deploy button)." ;;
  *) echo "Usage: $0 [--copy-openai-key] | tunnel <hostname>" >&2; exit 2 ;;
esac
