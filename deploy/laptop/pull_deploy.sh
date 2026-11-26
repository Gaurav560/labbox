#!/usr/bin/env bash
# Run every minute by labbox-prod-deploy.timer: when the production branch on GitHub has moved, check out its
# commit here and run that commit's release.sh. A commit that failed is not tried again until the branch moves.
# The work is in a function: bash reads all of it before the checkout below changes this file.
main() {
  set -euo pipefail
  local prod=/srv/labbox/prod sha live
  cd "$prod/src"
  # No production branch yet (nothing deployed through GitHub): nothing to do.
  git fetch -q origin +refs/heads/production:refs/remotes/origin/production 2>/dev/null || return 0
  sha="$(git rev-parse origin/production)"
  live="$(basename "$(readlink -f "$prod/current" 2>/dev/null)" 2>/dev/null || true)"
  [ "$sha" = "$live" ] && return 0
  [ "$sha" = "$(cat "$prod/failed" 2>/dev/null)" ] && return 0
  git checkout -q --detach "$sha"
  exec "$prod/src/deploy/laptop/release.sh" "$sha"
}
main "$@"
exit
