# Chapter 16: the standard library already knows statistics.
import statistics


def median_spend(amounts):
    if not amounts:
        return None
    return statistics.median(amounts)
