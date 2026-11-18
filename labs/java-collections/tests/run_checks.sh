#!/usr/bin/env bash
set -u
mkdir -p /tmp/build
if ! javac -d /tmp/build /check/workspace/*.java 2>/tmp/javac.err; then
  echo "Compile error:"; cat /tmp/javac.err
  for t in total_paise totals_by_merchant unique_merchants top_merchants; do
    echo "@@RESULT {\"task\": \"$t\", \"passed\": false, \"message\": \"Your code does not compile. See Output.\"}"
  done
  exit 0
fi
if ! javac -cp /tmp/build -d /tmp/build /check/tests/CheckPayments.java 2>/tmp/javac.err; then
  echo "Compile error:"; cat /tmp/javac.err
  for t in total_paise totals_by_merchant unique_merchants top_merchants; do
    echo "@@RESULT {\"task\": \"$t\", \"passed\": false, \"message\": \"A method signature changed: keep the names and types from the starter. See Output.\"}"
  done
  exit 0
fi
java -cp /tmp/build CheckPayments
