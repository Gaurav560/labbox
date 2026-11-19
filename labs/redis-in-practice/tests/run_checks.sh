#!/usr/bin/env bash
# Live check: runs in the checker container on the learner's lab network. Never runs learner code;
# it reads Redis and calls the learner's running app over HTTP.
python /check/tests/check.py
