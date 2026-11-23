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

    // TODO (task learn_threshold): try every delay in minutesLate as the threshold and return the one with the
    //   fewest mistakes (use mistakes(...) above). If two thresholds tie, return the smaller one.
    public static int bestThreshold(int[] minutesLate, boolean[] complained) {
        return 0;
    }
}
