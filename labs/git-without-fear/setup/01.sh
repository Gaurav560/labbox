#!/usr/bin/env bash
# Chapter 1 setup: the Trails website's first two files, not in git yet. The learner makes the repository.
set -euo pipefail
source /lab/setup/common.sh
fresh 01-why-version-control
mkdir trails && cd trails && trails_v1
