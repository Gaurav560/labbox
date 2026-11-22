#!/usr/bin/env bash
# check_file.sh FILE: is this file ready to use?
#   exists and is not empty  -> print "OK: FILE",      exit code 0
#   does not exist           -> print "MISSING: FILE" to standard error, exit code 1
#   exists but is empty      -> print "EMPTY: FILE"   to standard error, exit code 2
# TODO (task check_file): your script here. The file is "$1" (its name may contain spaces).
