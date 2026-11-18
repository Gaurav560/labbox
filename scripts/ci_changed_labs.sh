#!/usr/bin/env bash
# CI: build the base images and every lab changed since $BASE (default origin/main), then test-lab each.
# A change under images/ or tools/templates/ tests every lab.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${BASE:-origin/main}"
PY="${PYTHON:-python}"
cd "$ROOT"
changed="$(git diff --name-only "$BASE"...HEAD || true)"
if echo "$changed" | grep -qE '^(images/|tools/templates/|backend/app/(checker|containers|services|labs)\.py)'; then
  labs="$(ls -d labs/*/ | xargs -n1 basename)"
else
  labs="$(echo "$changed" | grep -oE '^labs/[^/]+' | sort -u | xargs -rn1 basename || true)"
fi
if [ -z "$labs" ]; then echo "No lab changed."; exit 0; fi
for base in base python java node go checker; do docker build -q -t "labbox/$base:v1" "images/$base" >/dev/null; done
grep -hE '^\s+image:' $(printf 'labs/%s/lab.yaml ' $labs) 2>/dev/null | awk '{print $2}' | sort -u | xargs -rn1 docker pull -q || true
status=0
for lab in $labs; do
  [ -f "labs/$lab/lab.yaml" ] || continue  # deleted
  echo "==> $lab"
  "$PY" tools/labbox_cli.py test-lab "$lab" || status=1
done
exit $status
