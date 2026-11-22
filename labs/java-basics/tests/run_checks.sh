#!/usr/bin/env bash
# Hidden checks for Java from zero. Each chapter lives in its own folder, compiled on its own, so code that
# does not compile in one chapter never breaks another chapter's check. LABBOX_CHAPTER (set by LabBox)
# limits the run to the chapter being checked; without it every chapter runs. A check whose class name starts
# with Self compiles the learner's files itself (chapter 1 checks each file separately).
set -u
W=/check/workspace

# chapter id | learner folder | check folder in tests/pkg | check class | tasks
CHAPTERS="
first-program|01-first-program|first|SelfCheckFirstProgram|hello_shelf fix_first_errors
01-methods|02-methods|.|CheckGreeter|greet longest_word
02-variables-and-types|03-variables-and-types|types|CheckTypes|percent format_rupees
03-decisions|04-decisions|decisions|CheckDecisions|grade leap_year
04-loops|05-loops|loops|CheckLoops|sum_to count_vowels
finding-bugs|06-finding-bugs|fines|CheckFines|fix_total_fines fix_can_borrow
05-strings|07-strings|words|CheckWords|count_words clean_name
06-arrays|08-arrays|arrays|CheckArrays|array_max reversed
07-classes-and-objects|09-classes-and-objects|objects|CheckObjects|point_distance bank_account
08-interfaces|10-interfaces|shapes|CheckShapes|areas total_area
09-collections|11-collections|collections|CheckCollections|top_n word_counts
generics-records-enums|12-generics-records-enums|modern|CheckModern|loan_record genre_enum
10-exceptions|13-exceptions|errors|CheckErrors|parse_age safe_sum
11-lambdas-and-streams|14-lambdas-and-streams|streams|CheckStreams|passing sort_by_length
12-files-and-cli|15-files-and-cli|files|CheckFiles|read_totals summary_cli
packages-and-maven|16-packages-and-maven|maven|SelfCheckMaven|package_catalog runnable_jar
testing|17-testing|testing|SelfCheckTesting|test_late_fee fix_renewal
13-capstone|capstone|capstone|CheckCapstone|fix_book monthly_report
"

fail_all() { # tasks message
  for t in $1; do echo "@@RESULT {\"task\": \"$t\", \"passed\": false, \"message\": \"$2\"}"; done
}

echo "$CHAPTERS" | while IFS='|' read -r chapter dir checkdir check tasks; do
  [ -z "$chapter" ] && continue
  if [ -n "${LABBOX_CHAPTER:-}" ] && [ "$chapter" != "$LABBOX_CHAPTER" ]; then continue; fi
  build=/tmp/build/$chapter
  mkdir -p "$build"
  if [ "$checkdir" = "." ]; then checks=/check/tests/$check.java; else checks="/check/tests/common/T.java /check/tests/pkg/$checkdir/$check.java"; fi
  if [[ "$check" == Self* ]]; then
    javac -d "$build" $checks && timeout 170 java -cp "$build" "$check" "$W/$dir"
    continue
  fi
  src=$(find "$W/$dir" -name '*.java' 2>/dev/null)
  if [ -z "$src" ]; then fail_all "$tasks" "Could not find the Java files for this chapter (folder $dir/) in your workspace."; continue; fi
  if ! javac -d "$build" $src 2>/tmp/javac.err; then
    echo "Compile error in $dir/:"; cat /tmp/javac.err
    fail_all "$tasks" "Not yet: your code in $dir/ does not compile. See Output for the exact line."
    continue
  fi
  if ! javac -cp "$build" -d "$build" $checks 2>/tmp/javac.err; then
    echo "The checks could not use your code in $dir/:"; cat /tmp/javac.err
    fail_all "$tasks" "Not yet: a class or method the checks need is missing or has a different shape in $dir/. See Output."
    continue
  fi
  timeout 25 java -Dlabbox.build="$build" -cp "$build" "$check"
done
