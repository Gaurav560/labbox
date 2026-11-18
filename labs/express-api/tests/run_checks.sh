#!/usr/bin/env bash
# Hidden checks: start the learner's server inside the check container, then call it.
cd /check/workspace
PORT=3000 node server.js > /tmp/server.log 2>&1 &
node /check/tests/check.js
