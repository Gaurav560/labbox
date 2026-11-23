package com.setu;

/** The two calculations at the heart of a transformer: softmax, and attention. */
public final class Attention {

    private Attention() {
    }

    // TODO (task softmax_temperature): turn scores into probabilities that add up to 1.
    //   Divide every score by temperature, subtract the largest of those (so Math.exp never overflows),
    //   take Math.exp of each, then divide each by their sum.
    public static double[] softmax(double[] scores, double temperature) {
        return new double[scores.length];
    }

    /** The dot product of two vectors: how much they point the same way. */
    public static double dot(double[] a, double[] b) {
        double sum = 0;
        for (int i = 0; i < a.length; i++) {
            sum += a[i] * b[i];
        }
        return sum;
    }

    // TODO (task attention_weights): how much one word (its query) attends to each word (their keys):
    //   score[i] = dot(query, keys[i]) / Math.sqrt(query.length), then softmax(score, 1.0).
    public static double[] weights(double[] query, double[][] keys) {
        return new double[keys.length];
    }
}
