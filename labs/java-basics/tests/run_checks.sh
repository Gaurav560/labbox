#!/usr/bin/env bash
# Hidden checks for Java from zero. Each chapter lives in its own folder (package), compiled on its own,
# so code that does not compile in one chapter never breaks another chapter's check. LABBOX_CHAPTER (set
# by LabBox) limits the run to the chapter being checked; without it every chapter runs.
set -u
W=/check/workspace

# chapter id | folder | check class | tasks
CHAPTERS="
01-methods|.|CheckGreeter|greet longest_word
02-variables-and-types|types|CheckTypes|percent format_rupees
03-decisions|decisions|CheckDecisions|grade leap_year
04-loops|loops|CheckLoops|sum_to count_vowels
05-strings|words|CheckWords|count_words clean_name
06-arrays|arrays|CheckArrays|array_max reversed
07-classes-and-objects|objects|CheckObjects|point_distance bank_account
08-interfaces|shapes|CheckShapes|areas total_area
09-collections|collections|CheckCollections|top_n word_counts
10-exceptions|errors|CheckErrors|parse_age safe_sum
11-lambdas-and-streams|streams|CheckStreams|passing sort_by_length
12-files-and-cli|files|CheckFiles|read_totals summary_cli
13-capstone|capstone|CheckCapstone|fix_book monthly_report
"

fail_all() { # tasks message
  for t in $1; do echo "@@RESULT {\"task\": \"$t\", \"passed\": false, \"message\": \"$2\"}"; done
}

echo "$CHAPTERS" | while IFS='|' read -r chapter dir check tasks; do
  [ -z "$chapter" ] && continue
  if [ -n "${LABBOX_CHAPTER:-}" ] && [ "$chapter" != "$LABBOX_CHAPTER" ]; then continue; fi
  build=/tmp/build/$chapter
  mkdir -p "$build"
  if [ "$dir" = "." ]; then src=$(ls $W/*.java 2>/dev/null); else src=$(find "$W/$dir" -name '*.java' 2>/dev/null); fi
  if [ -z "$src" ]; then fail_all "$tasks" "Could not find the Java files for this chapter (folder $dir/) in your workspace."; continue; fi
  if ! javac -d "$build" $src 2>/tmp/javac.err; then
    echo "Compile error in $dir/:"; cat /tmp/javac.err
    fail_all "$tasks" "Not yet: your code in $dir/ does not compile. See Output for the exact line."
    continue
  fi
  if [ "$dir" = "." ]; then checks=/check/tests/CheckGreeter.java; else checks="/check/tests/common/T.java /check/tests/pkg/$dir/$check.java"; fi
  if ! javac -cp "$build" -d "$build" $checks 2>/tmp/javac.err; then
    echo "The checks could not use your code in $dir/:"; cat /tmp/javac.err
    fail_all "$tasks" "Not yet: a class or method the checks need is missing or has a different shape in $dir/. See Output."
    continue
  fi
  timeout 25 java -Dlabbox.build="$build" -cp "$build" "$check"
done
