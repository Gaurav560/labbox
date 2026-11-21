# Chapter 18: a command-line program.
#   python summary.py expenses.csv --top 3
import argparse
import sys

from file_tools import read_totals

# TODO (task summary_top): read the arguments, print the top categories as "category: amount".
# TODO (task summary_errors): a friendly message and exit code 1 for a missing file; print nothing on import.
