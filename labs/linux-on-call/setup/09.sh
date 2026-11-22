#!/usr/bin/env bash
# Chapter 9: the server's files lose their permissions, as they did after a careless copy.
. /lab/setup/common.sh
fresh 09-disk-full
chmod 644 server/bin/*.sh server/config/*.env 2>/dev/null || true
