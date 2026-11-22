#!/usr/bin/env bash
# deploy.sh: build the site, then copy it into the folder named by the TARGET variable.
# Run it like this: TARGET=live bash deploy.sh
# TODO (task safe_deploy): this script keeps going after a failure, and runs even when TARGET is not set.
# Make it stop at the first error and refuse to run without TARGET.
./build.sh
rm -rf "$TARGET"/site
cp -r site "$TARGET"/
echo "Deployed to $TARGET"
