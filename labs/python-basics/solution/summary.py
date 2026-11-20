# Chapter 12: a command-line program.
#   python summary.py expenses.csv --top 3
import argparse
import sys

from file_tools import read_totals


def main() -> None:
    parser = argparse.ArgumentParser(description="The biggest spending categories")
    parser.add_argument("path")
    parser.add_argument("--top", type=int, default=3)
    args = parser.parse_args()
    try:
        totals = read_totals(args.path)
    except FileNotFoundError:
        print(f"File not found: {args.path}", file=sys.stderr)
        sys.exit(1)
    for category, amount in sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[: args.top]:
        print(f"{category}: {amount:.2f}")


if __name__ == "__main__":
    main()
