#!/usr/bin/env bash
# Run a lab's hidden checks once, the way a fresh check runs (no network), on a copy of starter/ or solution/.
#
#   tools/authoring/runcheck.sh <lab> starter|solution [chapter-id]
#
# Prints the @@RESULT lines. Faster than test-lab while writing one chapter: the starter should fail that
# chapter's tasks with kind messages, the solution should pass them. Labs with live checks or services still
# need `scripts/labbox test-lab <lab>`, which is the real gate. See COURSE_PRODUCTION.md, "Checks".
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
lab=$1; side=$2; chapter=${3:-}
image=$(grep -m1 '^image:' "$ROOT/labs/$lab/lab.yaml" | awk '{print $2}')
W=$(mktemp -d)
trap 'rm -rf "$W"' EXIT
cp -r "$ROOT/labs/$lab/$side/." "$W/"
chmod -R a+rwX "$W"
docker run --rm --network none -e LABBOX_CHAPTER="$chapter" \
  -v "$W:/check/workspace" -v "$ROOT/labs/$lab/tests:/check/tests:ro" -w /check/workspace \
  "$image" bash /check/tests/run_checks.sh
