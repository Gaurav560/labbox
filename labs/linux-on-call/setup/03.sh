#!/usr/bin/env bash
# Chapter 3: an observations file and an application log, both too long to read with your eyes.
. /lab/setup/common.sh
fresh 03-reading-files
rm -f observations.csv app.log recent.log answer-*.txt
python3 - <<'PY'
import random
rnd = random.Random(3)
targets = ["Crab Nebula", "Orion Nebula", "Jupiter", "Saturn", "Andromeda Galaxy", "Pleiades", "Vela Pulsar", "Cygnus A", "Sun"]
with open("observations.csv", "w") as f:
    f.write("obs_id,dish,target,minutes,signal\n")
    for i in range(1, 1249):
        f.write(f"{10000 + i},dish-{rnd.randint(1, 3)},{rnd.choice(targets)},{rnd.choice([5, 10, 15, 30, 60])},{rnd.choice(['strong', 'weak', 'good'])}\n")
msgs = ["capture started", "capture saved", "dish moved to target", "calibration done", "data copied to archive"]
with open("app.log", "w") as f:
    for i in range(600):
        h, m, s = (20 + i // 60) % 24, i % 60, (i * 7) % 60
        r = rnd.random()
        level, msg = ("ERROR", "receiver lost lock") if r < 0.04 else ("WARN", "wind is strong") if r < 0.12 else ("INFO", rnd.choice(msgs))
        day = 23 if h >= 20 else 24  # the night starts at 20:00 on the 23rd and ends at 06:00 on the 24th
        f.write(f"2026-11-{day} {h:02d}:{m:02d}:{s:02d} {level:5} capture={20000 + i} {msg}\n")
PY
