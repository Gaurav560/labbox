#!/usr/bin/env bash
# Chapter 13: the observatory's status app, ready to start.
. /lab/setup/common.sh
fresh 13-networking
rm -f server.py tonight.json tonight-fetched.json
write_server
