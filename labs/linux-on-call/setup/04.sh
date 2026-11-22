#!/usr/bin/env bash
# Chapter 4: a build script that writes to both output streams, and a list of last night's targets with repeats.
. /lab/setup/common.sh
fresh 04-pipes
rm -f build.sh targets.txt errors.txt tonight-targets.txt
cat > build.sh <<'SH'
#!/usr/bin/env bash
# Builds the Tara Observatory website. Progress goes to standard output, problems to standard error.
echo "Building target pages..."
echo "warning: photo crab-nebula.jpg is larger than 1 MB" >&2
echo "Building sky pages..."
echo "error: tonight.html links to a missing chart orion.png" >&2
echo "Packing photos..."
echo "error: about.html has no title" >&2
echo "Build finished with 2 errors."
exit 1
SH
chmod +x build.sh
python3 - <<'PY'
import random
rnd = random.Random(4)
targets = ["Crab Nebula", "Orion Nebula", "Jupiter", "Saturn", "Andromeda Galaxy", "Pleiades", "Vela Pulsar", "Cygnus A", "Moon"]
weights = [9, 4, 12, 10, 7, 5, 6, 3, 8]
with open("targets.txt", "w") as f:
    for _ in range(64):
        f.write(rnd.choices(targets, weights)[0] + "\n")
PY
