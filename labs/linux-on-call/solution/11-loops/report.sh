#!/usr/bin/env bash
# report.sh FOLDER: for every file captures-YYYY-MM-DD.csv in FOLDER, oldest first, print one line:
#   YYYY-MM-DD NUMBER_OF_CAPTURES
# Every file starts with one header line, which is not a capture.
for file in "$1"/captures-*.csv; do
  name=$(basename "$file" .csv)
  day=${name#captures-}
  lines=$(wc -l < "$file")
  echo "$day $((lines - 1))"
done
