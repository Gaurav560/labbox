#!/usr/bin/env bash
# Hidden checks for Spring AI. Each chapter's checks are JUnit tests (with a fake OpenAI server) copied into a temporary
# copy of that chapter's project and run offline with Maven. They print one @@RESULT line per task and
# never fail the build, so every task gets a result. A project that does not compile, or an app that does
# not start, fails only that chapter's tasks. LABBOX_CHAPTER (set by LabBox) limits the run to one chapter.
set -u
W=/check/workspace
T=/check/tests

# chapter id | project folder | tasks
CHAPTERS="
why-ai|01-why-ai|first_call model_alias
prompts|02-prompts|system_prompt prompt_template
options|03-options|chat_options token_usage
streaming|04-streaming|stream_answer stream_events
structured|05-structured|tour_plan exhibit_list
memory|06-memory|session_memory memory_window
tools|07-tools|opening_hours_tool show_times_tool
tool-safety|08-tool-safety|confirm_booking tool_context
advisors|09-advisors|usage_advisor language_advisor
mcp|10-mcp|mcp_server mcp_tools
embeddings|11-embeddings|cosine_similarity nearest_exhibit
vector-store|12-vector-store|add_documents search_cards
etl|13-etl|read_cards split_and_load
rag|14-rag|rag_answer cite_sources
"

fail_all() { # tasks message
  local m; m=$(printf '%s' "$2" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr '\n' ' ')
  for t in $1; do echo "@@RESULT {\"task\": \"$t\", \"passed\": false, \"message\": \"Not yet: $m\"}"; done
}

result() { # task passed message
  local m; m=$(printf '%s' "$3" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr '\n' ' ')
  echo "@@RESULT {\"task\": \"$1\", \"passed\": $2, \"message\": \"$m\"}"
}

# "tests failures" summed over the surefire reports of one Maven run.
counts() {
  local t=0 f=0 x a n
  for x in "$1"/target/surefire-reports/TEST-*.xml; do
    [ -f "$x" ] || continue
    a=$(grep -m1 -o '<testsuite [^>]*' "$x")
    for k in tests failures errors; do
      n=$(printf '%s' "$a" | sed -n "s/.* $k=\"\([0-9]*\)\".*/\1/p"); n=${n:-0}
      if [ "$k" = tests ]; then t=$((t + n)); else f=$((f + n)); fi
    done
  done
  echo "$t $f"
}

# Chapters whose task is to write tests: run the learner's own tests on the correct code, then again with
# the planted bug from tests/<chapter>/bug copied over the matching source file.
own_tests() { # chapter work tasks
  local chapter=$1 work=$2 tasks=$3 log=/tmp/check/$1.log MIN_TESTS TASK_TESTS TASK_BUG PASS_TESTS PASS_BUG MISS_BUG
  # shellcheck disable=SC1090
  . "$T/$chapter/own.env"
  (cd "$work" && MAVEN_OPTS="-Xmx256m" mvn -o -q -B test -DargLine="-Xmx384m" -Dspring.main.banner-mode=off > "$log" 2>&1)
  if grep -q "COMPILATION ERROR" "$log"; then
    why=$(grep -m1 -E "\[ERROR\] .*\.java:\[[0-9]+" "$log" | sed -E 's/.*\/src\/(main|test)\/java\///; s/^\[ERROR\] //')
    fail_all "$tasks" "the project does not compile: ${why:-see Output}."; tail -25 "$log"; return
  fi
  read -r n bad <<< "$(counts "$work")"
  if [ "$n" -lt "$MIN_TESTS" ]; then
    fail_all "$tasks" "found $n test(s) in src/test/java; write at least $MIN_TESTS."; return
  fi
  if [ "$bad" -gt 0 ]; then
    which=$(grep -m1 -oE "[A-Za-z0-9_]+\.[A-Za-z0-9_]+ -- Time elapsed.*<<< (FAILURE|ERROR)" "$log" | sed 's/ -- .*//')
    result "$TASK_TESTS" false "Not yet: $bad of your $n tests fail on the correct code${which:+ (first: $which)}. A test must pass when the code is right; see the Output for what it expected."
    result "$TASK_BUG" false "Not yet: first make your tests pass on the correct code."
    tail -40 "$log"; return
  fi
  [ "$n" = 1 ] && word=test || word=tests
  result "$TASK_TESTS" true "$n $word. $PASS_TESTS"
  local f pkg
  for f in "$T/$chapter/bug"/*.java; do
    pkg=$(sed -n 's/^package \([a-zA-Z0-9_.]*\);.*/\1/p' "$f" | head -1)
    cp "$f" "$work/src/main/java/$(echo "$pkg" | tr . /)/$(basename "$f")"
  done
  rm -rf "$work/target/surefire-reports"
  (cd "$work" && MAVEN_OPTS="-Xmx256m" mvn -o -q -B test -DargLine="-Xmx384m" -Dspring.main.banner-mode=off > "$log.bug" 2>&1)
  read -r n bad <<< "$(counts "$work")"
  if [ "$bad" -gt 0 ]; then result "$TASK_BUG" true "$PASS_BUG"; else result "$TASK_BUG" false "Not yet: $MISS_BUG"; fi
}

echo "$CHAPTERS" | while IFS='|' read -r chapter dir tasks; do
  [ -z "$chapter" ] && continue
  [ -n "${LABBOX_CHAPTER:-}" ] && [ "$LABBOX_CHAPTER" != "$chapter" ] && continue
  if [ ! -f "$W/$dir/pom.xml" ]; then fail_all "$tasks" "the project folder $dir is missing from your workspace."; continue; fi
  work=/tmp/check/$chapter
  rm -rf "$work"; mkdir -p "$work"
  (cd "$W/$dir" && tar --exclude=./target --exclude='./[0-9][0-9]-*' -cf - .) | (cd "$work" && tar -xf -)
  if [ -f "$T/$chapter/own.env" ]; then own_tests "$chapter" "$work" "$tasks"; continue; fi
  # The checks go into the package of the learner's @SpringBootApplication class, so Spring finds it.
  main=$(grep -rl --include=*.java "@SpringBootApplication" "$work/src/main/java" 2>/dev/null | head -1)
  if [ -z "$main" ]; then fail_all "$tasks" "no class with @SpringBootApplication was found in $dir/src/main/java."; continue; fi
  pkg=$(sed -n 's/^package \([a-zA-Z0-9_.]*\);.*/\1/p' "$main" | head -1)
  dest="$work/src/test/java/$(echo "$pkg" | tr . /)/check"
  mkdir -p "$dest"
  for f in "$T/common"/*.java "$T/$chapter"/*.java; do
    sed "s/^package com\.atlas\.check;/package $pkg.check;/" "$f" > "$dest/$(basename "$f")"
  done
  log=/tmp/check/$chapter.log
  (cd "$work" && MAVEN_OPTS="-Xmx256m" mvn -o -q -B test -Dsurefire.failIfNoSpecifiedTests=false \
      -Dtest="**/check/*Check" -DargLine="-Xmx384m" -Dspring.main.banner-mode=off > "$log" 2>&1)
  results=$(grep -o '@@RESULT .*' "$log")
  printf '%s\n' "$results" | grep -v '^$'
  missing=""
  for t in $tasks; do printf '%s' "$results" | grep -q "\"task\": \"$t\"" || missing="$missing $t"; done
  if [ -n "$missing" ]; then
    if grep -q "COMPILATION ERROR" "$log"; then
      why=$(grep -m1 -E "\[ERROR\] .*\.java:\[[0-9]+" "$log" | sed -E 's/.*\/src\/(main|test)\/java\///; s/^\[ERROR\] //')
      fail_all "$missing" "the project does not compile: ${why:-see Output}."
    else
      # The deepest "Caused by" is the real reason; drop its exception class name so it reads plainly.
      why=$(grep -E "^Caused by: " "$log" | tail -1 | sed -E 's/^Caused by: [A-Za-z0-9_.$]+: //' | cut -c1-220)
      [ -n "$why" ] || why=$(grep -m1 -E "Application run failed|APPLICATION FAILED TO START" -A2 "$log" | grep -m1 -vE "^\s*$" | cut -c1-220)
      fail_all "$missing" "the app did not start in the check: ${why:-see Output}."
    fi
    echo "---- $chapter: the last lines of the build ----"; tail -25 "$log"
  fi
done
