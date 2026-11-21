#!/usr/bin/env bash
# Hidden checks for Spring Boot. Each chapter's checks are JUnit tests (MockMvc) copied into a temporary
# copy of that chapter's project and run offline with Maven. They print one @@RESULT line per task and
# never fail the build, so every task gets a result. A project that does not compile, or an app that does
# not start, fails only that chapter's tasks. LABBOX_CHAPTER (set by LabBox) limits the run to one chapter.
set -u
W=/check/workspace
T=/check/tests

# chapter id | project folder | tasks
CHAPTERS="
00-what-is-a-framework|.|app_name
01-first-endpoints|.|hello merchants
02-app-startup|02-app-startup|component_scan greeting_property
03-beans|03-beans|price_service one_counter
04-layers|04-layers|thin_controller budget_products
05-reading-the-request|05-reading-the-request|product_by_id search_products
"

fail_all() { # tasks message
  local m; m=$(printf '%s' "$2" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr '\n' ' ')
  for t in $1; do echo "@@RESULT {\"task\": \"$t\", \"passed\": false, \"message\": \"Not yet: $m\"}"; done
}

echo "$CHAPTERS" | while IFS='|' read -r chapter dir tasks; do
  [ -z "$chapter" ] && continue
  [ -n "${LABBOX_CHAPTER:-}" ] && [ "$LABBOX_CHAPTER" != "$chapter" ] && continue
  if [ ! -f "$W/$dir/pom.xml" ]; then fail_all "$tasks" "the project folder $dir is missing from your workspace."; continue; fi
  work=/tmp/check/$chapter
  rm -rf "$work"; mkdir -p "$work"
  (cd "$W/$dir" && tar --exclude=./target --exclude='./[0-9][0-9]-*' -cf - .) | (cd "$work" && tar -xf -)
  # The checks go into the package of the learner's @SpringBootApplication class, so Spring finds it.
  main=$(grep -rl --include=*.java "@SpringBootApplication" "$work/src/main/java" 2>/dev/null | head -1)
  if [ -z "$main" ]; then fail_all "$tasks" "no class with @SpringBootApplication was found in $dir/src/main/java."; continue; fi
  pkg=$(sed -n 's/^package \([a-zA-Z0-9_.]*\);.*/\1/p' "$main" | head -1)
  dest="$work/src/test/java/$(echo "$pkg" | tr . /)/check"
  mkdir -p "$dest"
  for f in "$T/common"/*.java "$T/$chapter"/*.java; do
    sed "s/^package com\.shop\.check;/package $pkg.check;/" "$f" > "$dest/$(basename "$f")"
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
      why=$(grep -m1 -E "\[ERROR\] .*\.java:\[[0-9]+" "$log" | sed 's/.*\/src\/main\/java\///; s/^\[ERROR\] //')
      fail_all "$missing" "the project does not compile: ${why:-see Output}."
    else
      why=$(grep -m1 -E "Caused by: |Application run failed|APPLICATION FAILED TO START" -A2 "$log" | grep -m1 -vE "^\s*$" | cut -c1-220)
      fail_all "$missing" "the app did not start in the check: ${why:-see Output}."
    fi
    echo "---- $chapter: the last lines of the build ----"; tail -25 "$log"
  fi
done
