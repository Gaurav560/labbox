#!/usr/bin/env bash
# Hidden checks for Go from zero. Each chapter lives in its own package, so a chapter that does not
# compile never breaks another chapter's check. LABBOX_CHAPTER (set by LabBox) limits the run to the
# chapter being checked; without it every chapter runs.
set -u
cd /check/workspace

# chapter id | package folder | test file | tasks
CHAPTERS="
hello-go|01-hello-go|gorun|hello_parcel fix_first_errors
01-first-program|02-functions|pkg/hello|greeting total_minutes
02-numbers-and-text|03-numbers-and-text|pkg/numbers|percent format_rupees
03-decisions|04-decisions|pkg/decisions|grade leap_year
04-loops|05-loops|pkg/loops|sum_to count_vowels
finding-bugs|06-finding-bugs|pkg/van|fix_total_weight fix_can_load
01-slices-and-errors|07-slices-and-errors|pkg/till|total parse_amount
06-strings|08-strings|pkg/words|clean_name count_words
07-more-slices|09-more-slices|pkg/slicetools|top_n unique
02-maps-and-structs|10-maps-and-structs|pkg/orders|count_by_item busiest
11-pointers|11-pointers|pkg/wallet|deposit swap
09-methods-and-interfaces|12-methods-and-interfaces|pkg/shapes|areas total_area
10-errors-in-depth|13-errors-in-depth|pkg/bank|withdraw parse_age
packages-and-json|14-packages-and-json|pkg/manifest|save_manifest load_manifest
12-files-and-cli|15-files-and-cli|pkg/expenses|read_totals summary_cli
13-goroutines|16-goroutines|pkg/concurrent|fetch_all word_counts
testing|17-testing|gotest|fix_next_stop test_eta
capstone|18-capstone|pkg/report|depot_report busiest_depot
"

fail_all() { # tasks message
  for t in $1; do echo "@@RESULT {\"task\": \"$t\", \"passed\": false, \"message\": \"$2\"}"; done
}

echo "$CHAPTERS" | while IFS='|' read -r chapter dir tests tasks; do
  [ -z "$chapter" ] && continue
  if [ -n "${LABBOX_CHAPTER:-}" ] && [ "$chapter" != "$LABBOX_CHAPTER" ]; then continue; fi
  if [ ! -d "$dir" ]; then fail_all "$tasks" "Could not find the folder $dir/ in your workspace."; continue; fi
  if [ "$tests" = "gotest" ]; then  # the learner's own tests: go test on copies in a scratch module
    (cd /tmp && go build -o /tmp/gotest-check /check/tests/gotest/check.go) && /tmp/gotest-check "/check/workspace/$dir"
    continue
  fi
  if [ "$tests" = "gorun" ]; then  # small programs: run them with go run and compare their output
    (cd /tmp && go build -o /tmp/gorun-check /check/tests/gorun/check.go) && /tmp/gorun-check "/check/workspace/$dir"
    continue
  fi
  if [ "$tests" = "." ]; then src=/check/tests/labbox_check_test.go; else src=/check/tests/$tests/labbox_check_test.go; fi
  cp "$src" "$dir/labbox_check_test.go"
  if ! go vet "./$dir" > /tmp/vet.log 2>&1; then
    echo "Build failed in $dir/:"; cat /tmp/vet.log
    fail_all "$tasks" "Your code in $dir/ does not compile. See Output for the exact line."
    continue
  fi
  out=$(go test -count=1 -v -run 'LabboxCheck' "./$dir" 2>&1)
  echo "$out" | grep -E '^@@RESULT' || true
  # A fatal error (like two goroutines writing one map) kills the tests before every task reports:
  # say so for each missing task instead of leaving it blank.
  crash=$(echo "$out" | grep -m1 -E '^(fatal error|panic):' || true)
  for t in $tasks; do
    if ! echo "$out" | grep -q "\"task\":\"$t\""; then
      case "$crash" in
        *"concurrent map"*) why="Your program crashed with \\\"$crash\\\": several goroutines wrote to one map at the same time. Protect it with a sync.Mutex (or use a channel)." ;;
        "") why="The tests stopped before reaching this task. See Output." ;;
        *) why="Your program crashed before this task could be checked: $crash" ;;
      esac
      echo "$out" | grep -E '^(fatal error|panic):' | head -3
      echo "@@RESULT {\"task\": \"$t\", \"passed\": false, \"message\": \"$why\"}"
    fi
  done
done
