#!/usr/bin/env bash
# fix_perms.sh DIR: fix the permissions of a server folder.
#   - every .sh file in DIR/bin must be executable
#   - DIR/config/secrets.env must be readable and writable by its owner only
chmod +x "$1"/bin/*.sh
chmod 600 "$1/config/secrets.env"
