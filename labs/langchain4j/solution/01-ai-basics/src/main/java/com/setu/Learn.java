package com.setu;

/** Machine learning in one method: instead of writing the rule, find it in examples. */
public final class Learn {

    private Learn() {
    }

    /** How many examples the rule "late by at least threshold minutes means a complaint" gets wrong. */
    public static int mistakes(int threshold, int[] minutesLate, boolean[] complained) {
        int wrong = 0;
        for (int i = 0; i < minutesLate.length; i++) {
            boolean predicted = minutesLate[i] >= threshold;
            if (predicted != complained[i]) {
                wrong++;
            }
        }
        return wrong;
    }

    /** The threshold, taken from the examples, that gets the fewest examples wrong (the smaller one on a tie). */
    public static int bestThreshold(int[] minutesLate, boolean[] complained) {
        int best = Integer.MAX_VALUE;
        int fewest = Integer.MAX_VALUE;
        for (int candidate : minutesLate) {
            int wrong = mistakes(candidate, minutesLate, complained);
            if (wrong < fewest || (wrong == fewest && candidate < best)) {
                best = candidate;
                fewest = wrong;
            }
        }
        return best;
    }
}
