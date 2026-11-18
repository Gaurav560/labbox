#!/usr/bin/env bash
# Build the Docker image for every lab in labs/*/ using the image tag from its lab.yaml.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
for dir in "$ROOT"/labs/*/; do
  [ -f "$dir/Dockerfile" ] || continue
  image="$(grep -E '^image:' "$dir/lab.yaml" | awk '{print $2}')"
  if [ -z "$image" ]; then
    echo "No image in $dir/lab.yaml" >&2; exit 1
  fi
  echo "==> Building $image from $dir"
  docker build -t "$image" "$dir"
done
echo "All lab images built."
