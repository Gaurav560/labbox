package com.setu;

/** The two calculations at the heart of a transformer: softmax, and attention. */
public final class Attention {

    private Attention() {
    }

    /** Scores to probabilities: a low temperature sharpens them, a high one flattens them. */
    public static double[] softmax(double[] scores, double temperature) {
        double[] out = new double[scores.length];
        double max = Double.NEGATIVE_INFINITY;
        for (double s : scores) {
            max = Math.max(max, s / temperature);
        }
        double sum = 0;
        for (int i = 0; i < scores.length; i++) {
            out[i] = Math.exp(scores[i] / temperature - max);
            sum += out[i];
        }
        for (int i = 0; i < out.length; i++) {
            out[i] /= sum;
        }
        return out;
    }

    /** The dot product of two vectors: how much they point the same way. */
    public static double dot(double[] a, double[] b) {
        double sum = 0;
        for (int i = 0; i < a.length; i++) {
            sum += a[i] * b[i];
        }
        return sum;
    }

    /** Scaled dot-product attention weights, from "Attention Is All You Need" (2017). */
    public static double[] weights(double[] query, double[][] keys) {
        double[] scores = new double[keys.length];
        for (int i = 0; i < keys.length; i++) {
            scores[i] = dot(query, keys[i]) / Math.sqrt(query.length);
        }
        return softmax(scores, 1.0);
    }
}
