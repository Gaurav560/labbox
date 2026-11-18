#!/usr/bin/env bash
# Hidden checks: the test file joins the learner's package in the copied workspace, prints @@RESULT lines.
set -u
cd /check/workspace
cp /check/tests/labbox_check_test.go ./labbox_check_test.go
if ! go vet . > /tmp/vet.log 2>&1; then
  echo "Build failed:"; cat /tmp/vet.log
  for t in double; do echo "@@RESULT {\"task\": \"$t\", \"passed\": false, \"message\": \"Your code does not compile. See Output.\"}"; done
  exit 0
fi
go test -count=1 -v -run 'LabboxCheck' . 2>&1 | grep -E '^@@RESULT|panic|FAIL' || true
