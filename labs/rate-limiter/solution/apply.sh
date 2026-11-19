#!/usr/bin/env bash
# Used only by `labbox test-lab`: start both copies of the solution behind the load balancer.
set -euo pipefail
cd /workspace
setsid bash run.sh > /tmp/run.log 2>&1 < /dev/null
