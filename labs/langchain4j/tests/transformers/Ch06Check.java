package com.setu.check;

import java.util.Arrays;

import org.junit.jupiter.api.Test;

import com.setu.Attention;

class Ch06Check {

    static double[] ref(double[] s, double t) {
        double max = Arrays.stream(s).map(x -> x / t).max().orElse(0);
        double[] o = new double[s.length];
        double sum = 0;
        for (int i = 0; i < s.length; i++) { o[i] = Math.exp(s[i] / t - max); sum += o[i]; }
        for (int i = 0; i < s.length; i++) o[i] /= sum;
        return o;
    }

    static boolean close(double[] a, double[] b) {
        if (a == null || a.length != b.length) return false;
        for (int i = 0; i < a.length; i++) if (Double.isNaN(a[i]) || Math.abs(a[i] - b[i]) > 1e-9) return false;
        return true;
    }

    @Test
    void softmaxTemperature() {
        R.task("softmax_temperature", () -> {
            double[][] scores = {{4.0, 2.5, 2.0, -1.0}, {1, 1, 1}, {0.5, -0.5}};
            for (double[] s : scores) {
                for (double t : new double[] {1.0, 0.2, 2.0}) {
                    double[] got = Attention.softmax(s, t);
                    if (!close(got, ref(s, t))) {
                        String hint = t != 1.0 && close(Attention.softmax(s, 1.0), ref(s, 1.0))
                                ? "Right at temperature 1, wrong at " + t + ": divide every score by the temperature first."
                                : "exp of each (score / temperature, minus the largest), each divided by the sum of them.";
                        R.fail("softmax_temperature", "softmax(" + Arrays.toString(s) + ", " + t + ") is wrong. " + hint,
                                Arrays.toString(ref(s, t)), Arrays.toString(got));
                        return;
                    }
                }
            }
            double[] big = Attention.softmax(new double[] {1000, 999}, 1.0);
            if (!close(big, ref(new double[] {1000, 999}, 1.0))) {
                R.fail("softmax_temperature", "With scores 1000 and 999, Math.exp(1000) is Infinity, so the result breaks. Subtract the largest score before Math.exp.",
                        Arrays.toString(ref(new double[] {1000, 999}, 1.0)), Arrays.toString(big));
                return;
            }
            R.pass("softmax_temperature", "This is the temperature knob of every chat model: low makes the likeliest word near certain, high spreads the chances.");
        });
    }

    @Test
    void attentionWeights() {
        R.task("attention_weights", () -> {
            double[] q = {1.0, 1.0, 0.0};
            double[][] k = {{1.0, 0.9, 0.1}, {0.1, 0.2, 1.0}, {0.8, 0.7, 0.3}};
            double[] scores = new double[k.length];
            for (int i = 0; i < k.length; i++) scores[i] = Attention.dot(q, k[i]) / Math.sqrt(q.length);
            double[] want = ref(scores, 1.0);
            double[] got = Attention.weights(q, k);
            if (!close(got, want)) {
                double[] unscaled = new double[k.length];
                for (int i = 0; i < k.length; i++) unscaled[i] = Attention.dot(q, k[i]);
                String hint = close(got, ref(unscaled, 1.0))
                        ? "Almost: divide each dot product by Math.sqrt(query.length) before the softmax (that is the scaling)."
                        : "For each key: dot(query, key) / Math.sqrt(query.length); then softmax of those scores at temperature 1.";
                R.fail("attention_weights", "Attention.weights is not right. " + hint, Arrays.toString(want), Arrays.toString(got));
                return;
            }
            R.pass("attention_weights", "Scaled dot-product attention: how each word decides which other words matter, inside every transformer.");
        });
    }
}
