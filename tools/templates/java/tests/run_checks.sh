#!/usr/bin/env bash
set -u
mkdir -p /tmp/build
if ! javac -d /tmp/build /check/workspace/*.java 2>/tmp/javac.err; then
  echo "Compile error:"; cat /tmp/javac.err
  echo '@@RESULT {"task": "twice", "passed": false, "message": "Your code does not compile. See Output."}'
  exit 0
fi
javac -cp /tmp/build -d /tmp/build /check/tests/CheckTwice.java
java -cp /tmp/build CheckTwice
