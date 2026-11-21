#!/usr/bin/env bash
# Rewritten chapters (one folder each) are checked by checks.py; the rest still by check.py.
# LABBOX_CHAPTER (set by LabBox) limits checks.py to that chapter; check.py runs only for its own chapters.
cd /check/workspace
python /check/tests/checks.py
case "${LABBOX_CHAPTER:-}" in
  first-program|02-numbers-and-text|01-functions|03-decisions|04-loops|finding-bugs|sorting-and-comprehensions) ;;
  *) python /check/tests/check.py ;;
esac
