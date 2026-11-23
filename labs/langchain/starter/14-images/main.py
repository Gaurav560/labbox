"""Chapter 14: run with  python main.py"""
from pathlib import Path

from leaf import leaf_report

photo = Path("leaf.jpg").read_bytes()
print(f"leaf.jpg: {len(photo):,} bytes")
report = leaf_report("These spots appeared on my grape leaves this week. What could it be?", photo)
for field, value in report.model_dump().items():
    print(f"{field:11} {value}")
