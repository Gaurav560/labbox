#!/usr/bin/env bash
# Chapter 11: camera photos with ugly names, and a week of capture files.
. /lab/setup/common.sh
fresh 11-loops
rm -rf photos captures
mkdir -p photos captures
for n in 0001 0002 0003 0004 0005 0006 0007 0008 0009 0010 0011 0012; do printf 'photo %s\n' "$n" > "photos/IMG_$n.JPG"; done
python3 - <<'PY'
import random
rnd = random.Random(11)
for day, n in zip(range(17, 23), [212, 198, 240, 251, 305, 187]):
    with open(f"captures/captures-2026-11-{day}.csv", "w") as f:
        f.write("capture_id,dish,target\n")
        for i in range(n):
            f.write(f"{day * 1000 + i},dish-{rnd.randint(1, 3)},{rnd.choice(['Crab Nebula', 'Jupiter', 'Vela Pulsar', 'Cygnus A'])}\n")
PY
