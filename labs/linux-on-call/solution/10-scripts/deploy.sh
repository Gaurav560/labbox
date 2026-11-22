#!/usr/bin/env bash
# deploy.sh: build the site, then copy it into the folder named by the TARGET variable.
# Run it like this: TARGET=live bash deploy.sh
set -euo pipefail
./build.sh
rm -rf "$TARGET"/site
cp -r site "$TARGET"/
echo "Deployed to $TARGET"
