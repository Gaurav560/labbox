#!/usr/bin/env bash
# Live check: runs in the checker container on the learner's lab network. Every change it makes to try
# the learner's database is rolled back.
python /check/tests/check.py
