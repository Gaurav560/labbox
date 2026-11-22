#!/usr/bin/env bash
# check_file.sh FILE: is this file ready to use?
#   exists and is not empty  -> print "OK: FILE",      exit code 0
#   does not exist           -> print "MISSING: FILE" to standard error, exit code 1
#   exists but is empty      -> print "EMPTY: FILE"   to standard error, exit code 2
file="$1"
if [ ! -e "$file" ]; then
  echo "MISSING: $file" >&2
  exit 1
elif [ ! -s "$file" ]; then
  echo "EMPTY: $file" >&2
  exit 2
fi
echo "OK: $file"
