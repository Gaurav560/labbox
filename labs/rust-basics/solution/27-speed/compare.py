"""The same job in Python, for comparison:  python3 compare.py   (run cargo run --release first, to make the file)."""
import time

start = time.perf_counter()
totals = {}
with open("data/quarter.log") as f:
    for line in f:
        turbine, _, power = line.partition(",")[0], None, line.rsplit(",", 1)[1]
        totals[turbine] = totals.get(turbine, 0.0) + float(power) * 10 / 60
elapsed = time.perf_counter() - start
print(f"T07: {totals['T07']:.0f} kWh")
print(f"read and totalled in {elapsed * 1000:.1f} ms")
