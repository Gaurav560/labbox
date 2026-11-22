#!/usr/bin/env bash
# Live check: the workspace is mounted read-only; scripts run in scratch copies inside the check container.
cd /check/workspace
python /check/tests/check.py
