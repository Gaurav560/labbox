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
00-what-is-spring-boot|00-what-is-spring-boot|app_name
01-how-the-web-works|01-how-the-web-works|http_status http_methods
02-maven-and-the-project|02-maven-and-the-project|add_actuator project_identity
03-first-endpoints|03-first-endpoints|hello merchants
04-app-startup|04-app-startup|component_scan greeting_property
05-beans|05-beans|price_service one_counter
06-dependency-injection|06-dependency-injection|primary_gateway all_gateways
07-configuration-and-profiles|07-configuration-and-profiles|shop_properties prod_profile
08-auto-configuration|08-auto-configuration|backs_off on_property
09-bean-lifecycle|09-bean-lifecycle|post_construct prototype_scope
11-reading-the-request|11-reading-the-request|product_by_id search_products
12-request-bodies|12-request-bodies|create_product product_view
13-status-codes|13-status-codes|created_201 delete_204
14-layers|14-layers|thin_controller budget_products
16-validation|16-validation|validate_product validate_customer
17-errors|17-errors|not_found_problem validation_problem
19-database|19-database|product_entity unique_sku
20-repositories|20-repositories|find_by_category sku_conflict
21-relationships|21-relationships|order_items fix_n_plus_one
22-paging|22-paging|paged_products price_range
23-transactions|23-transactions|place_order_atomic rollback_checked
24-migrations|24-migrations|add_category_column set_categories
25-testing-controllers|25-testing-controllers|controller_test catches_bug
26-testing-data|26-testing-data|repository_test catches_query_bug
27-logging-and-health|27-logging-and-health|health_info log_warning
28-security|28-security|public_and_protected admin_only
29-calling-services|29-calling-services|fetch_stock handle_supplier_errors
30-capstone|30-capstone|checkout checkout_errors
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
