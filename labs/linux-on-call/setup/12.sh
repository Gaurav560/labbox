#!/usr/bin/env bash
# Chapter 12: a small command of the observatory's own, not on the PATH and not executable yet.
. /lab/setup/common.sh
fresh 12-environment
rm -rf bin
mkdir -p bin
printf '#!/usr/bin/env bash\necho "Tara: 2 of 3 dishes online, tracking the Crab Nebula"\n' > bin/tara-status
chmod 644 bin/tara-status
