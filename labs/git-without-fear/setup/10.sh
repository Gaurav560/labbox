#!/usr/bin/env bash
# Chapter 10 setup: a server repository and your clone, ready for a pull request.
set -euo pipefail
source /lab/setup/common.sh
fresh 10-pull-request
git init -q trails-start && cd trails-start && trails_v1
git add README.md trails.md && commit "2026-11-18T09:00:00+05:30" "Add the README and two trails"
cd .. && git clone -q --bare trails-start server/trails.git && rm -rf trails-start
git clone -q server/trails.git trails
