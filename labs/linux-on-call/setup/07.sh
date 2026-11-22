#!/usr/bin/env bash
# Chapter 7: a script that will not run yet, and a private key that everyone can read.
. /lab/setup/common.sh
fresh 07-permissions
rm -rf hello.sh keys
mkdir -p keys
printf '#!/usr/bin/env bash\necho "Hello from the Tara Observatory server, $(whoami)!"\n' > hello.sh
printf -- '-----BEGIN PRACTICE KEY-----\nThis is a practice file, not a real key.\n-----END PRACTICE KEY-----\n' > keys/deploy-key.pem
printf 'The deploy key opens the archive server, where every night of sky data is kept.\n' > keys/README.txt
chmod 644 hello.sh keys/deploy-key.pem keys/README.txt
chmod 755 keys
