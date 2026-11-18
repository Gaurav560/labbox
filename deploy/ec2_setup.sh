#!/usr/bin/env bash
# One-time host setup for LabBox on Ubuntu 24.04 (x86_64). Safe to run more than once.
# Usage: sudo bash deploy/ec2_setup.sh
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Run with sudo: sudo bash $0" >&2
  exit 1
fi

APP_USER="${APP_USER:-ubuntu}"
export DEBIAN_FRONTEND=noninteractive
ARCH="$(dpkg --print-architecture)"
CODENAME="$(. /etc/os-release && echo "$VERSION_CODENAME")"

echo "==> 1. System update"
apt-get update
apt-get upgrade -y
apt-get install -y ca-certificates curl gnupg

echo "==> 2. Docker Engine (official repo)"
install -m 0755 -d /etc/apt/keyrings
if [ ! -f /etc/apt/keyrings/docker.asc ]; then
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
fi
echo "deb [arch=$ARCH signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $CODENAME stable" \
  > /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin
systemctl enable --now docker
usermod -aG docker "$APP_USER"

echo "==> 3. gVisor (runsc)"
if [ ! -f /usr/share/keyrings/gvisor-archive-keyring.gpg ]; then
  curl -fsSL https://gvisor.dev/archive.key | gpg --dearmor -o /usr/share/keyrings/gvisor-archive-keyring.gpg
fi
echo "deb [arch=$ARCH signed-by=/usr/share/keyrings/gvisor-archive-keyring.gpg] https://storage.googleapis.com/gvisor/releases release main" \
  > /etc/apt/sources.list.d/gvisor.list
apt-get update
apt-get install -y runsc
runsc install
systemctl restart docker
docker run --rm --runtime=runsc hello-world >/dev/null && echo "gVisor OK: hello-world ran under runsc"

echo "==> 4. Python 3.12, Node 22, Nginx, iptables-persistent"
echo "iptables-persistent iptables-persistent/autosave_v4 boolean true" | debconf-set-selections
echo "iptables-persistent iptables-persistent/autosave_v6 boolean true" | debconf-set-selections
apt-get install -y python3.12 python3.12-venv python3-pip nginx iptables-persistent git
if ! command -v node >/dev/null || ! node --version | grep -q '^v22\.'; then
  curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
  apt-get install -y nodejs
fi

echo "==> 5. Block containers from the EC2 metadata service"
iptables -C DOCKER-USER -d 169.254.169.254 -j DROP 2>/dev/null \
  || iptables -I DOCKER-USER -d 169.254.169.254 -j DROP
if ip6tables -L DOCKER-USER >/dev/null 2>&1; then
  ip6tables -C DOCKER-USER -d fd00:ec2::254 -j DROP 2>/dev/null \
    || ip6tables -I DOCKER-USER -d fd00:ec2::254 -j DROP
fi
netfilter-persistent save
docker run --rm --runtime=runsc --network bridge curlimages/curl:8.10.1 -s -m 3 http://169.254.169.254/ \
  && echo "WARNING: metadata service is reachable from containers!" \
  || echo "Metadata service blocked for containers"

echo "==> 6. Data folders"
mkdir -p /srv/labbox/volumes /srv/labbox/checks
chown "$APP_USER:$APP_USER" /srv/labbox /srv/labbox/volumes /srv/labbox/checks
mkdir -p /opt/labbox
chown "$APP_USER:$APP_USER" /opt/labbox

cat <<NEXT

==> Done. Next steps (as $APP_USER, after logging out and back in so the docker group applies):

  git clone <repo> /opt/labbox && cd /opt/labbox
  bash scripts/build_lab_images.sh
  cd backend && python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
  cp .env.example .env    # set JWT_SECRET, CONTAINER_RUNTIME=runsc, CORS_ORIGINS
  cd ../frontend && npm ci && npm run build
  sudo cp ../deploy/labbox.service /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl enable --now labbox
  sudo cp ../deploy/nginx.conf /etc/nginx/sites-available/labbox
  sudo ln -sf /etc/nginx/sites-available/labbox /etc/nginx/sites-enabled/labbox
  sudo rm -f /etc/nginx/sites-enabled/default && sudo nginx -t && sudo systemctl reload nginx

NEXT
