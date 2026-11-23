#!/usr/bin/env bash
# Hidden checks for LangGraph. Each chapter's checks are pytest files, run inside a temporary copy of that
# chapter's folder with a fake OpenAI server (no network, no cost). They print one @@RESULT line per task and never
# fail the run, so every task gets a result. LABBOX_CHAPTER (set by LabBox) limits the run to one chapter.
set -u
W=/check/workspace
T=/check/tests

# chapter id | project folder | tasks
CHAPTERS="
why-graphs|01-why-graphs|first_graph trace_steps
state|02-state|log_reducer severity_reducer
branches|03-branches|route_by_kind retry_loop
model-nodes|04-model-nodes|triage_node reply_node
patterns|05-patterns|parallel_branches evaluator_loop
send-command|06-send-command|fan_out command_goto
"

fail_all() { # tasks message
  local m; m=$(printf '%s' "$2" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr '\n' ' ')
  for t in $1; do echo "@@RESULT {\"task\": \"$t\", \"passed\": false, \"message\": \"Not yet: $m\"}"; done
}

echo "$CHAPTERS" | while IFS='|' read -r chapter dir tasks; do
  [ -z "$chapter" ] && continue
  [ -n "${LABBOX_CHAPTER:-}" ] && [ "$LABBOX_CHAPTER" != "$chapter" ] && continue
  if [ ! -d "$W/$dir" ]; then fail_all "$tasks" "the folder $dir is missing from your workspace."; continue; fi
  work=/tmp/check/$chapter
  rm -rf "$work"; mkdir -p "$work"
  (cd "$W/$dir" && tar --exclude=__pycache__ --exclude=.venv -cf - .) | (cd "$work" && tar -xf -)
  mkdir -p "$work/_checks"
  cp "$T/common"/*.py "$T/$chapter"/*.py "$work/_checks/"
  log=/tmp/check/$chapter.log
  (cd "$work" && timeout 200 python3 -m pytest -q -s -p no:cacheprovider --rootdir="$work/_checks" "$work/_checks" > "$log" 2>&1)
  results=$(grep -o '@@RESULT .*' "$log")
  printf '%s\n' "$results" | grep -v '^$'
  missing=""
  for t in $tasks; do printf '%s' "$results" | grep -q "\"task\": \"$t\"" || missing="$missing $t"; done
  if [ -n "$missing" ]; then
    why=$(grep -m1 -E "^E +[A-Za-z]+Error|SyntaxError|IndentationError|ModuleNotFoundError" "$log" | sed -E 's/^E +//' | cut -c1-220)
    fail_all "$missing" "the checks could not run your code: ${why:-see Output}."
    echo "---- $chapter: the last lines ----"; tail -20 "$log"
  fi
done
