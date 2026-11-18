#!/usr/bin/env bash
set -u
mkdir -p /tmp/build
if ! javac -d /tmp/build /check/workspace/*.java 2>/tmp/javac.err; then
  echo "Compile error:"; cat /tmp/javac.err
  # Report every task as failed with a compile message
  for t in greet longest_word; do
    echo "@@RESULT {\"task\": \"$t\", \"passed\": false, \"message\": \"Your code does not compile. See Output.\"}"
  done
  exit 0
fi
javac -cp /tmp/build -d /tmp/build /check/tests/CheckGreeter.java
java -cp /tmp/build CheckGreeter
