package com.setu.check;

import java.util.Arrays;
import java.util.Random;

import org.junit.jupiter.api.Test;

import com.setu.Neuron;

class Ch02Check {

    @Test
    void neuronFire() {
        R.task("neuron_fire", () -> {
            Object[][] cases = {
                {new double[] {1, 0}, new double[] {0.5, 0.5}, -0.4, 1},
                {new double[] {1, 1}, new double[] {0.5, -0.5}, 0.0, 0},
                {new double[] {0, 0}, new double[] {0.9, 0.9}, -0.1, 0},
                {new double[] {1, 1, 1}, new double[] {0.2, 0.3, 0.4}, -0.8, 1},
                {new double[] {2, 0}, new double[] {-1, 5}, 1.0, 0}};
            for (Object[] c : cases) {
                int got = Neuron.fire((double[]) c[0], (double[]) c[1], (double) c[2]);
                if (got != (int) c[3]) {
                    String hint = c[2].equals(0.0)
                            ? "Here the total is exactly 0: the neuron fires only when it is greater than 0."
                            : "Add up input times weight for every input, add the bias, and fire when the total is above 0.";
                    R.fail("neuron_fire", "fire(" + Arrays.toString((double[]) c[0]) + ", " + Arrays.toString((double[]) c[1]) + ", " + c[2] + ") is wrong. " + hint,
                            String.valueOf(c[3]), String.valueOf(got));
                    return;
                }
            }
            R.pass("neuron_fire", "A weighted sum and a threshold: every neural network is built from this one calculation.");
        });
    }

    static String mistakes(double[][] xs, int[] ys, Neuron.Weights w) {
        for (int i = 0; i < xs.length; i++) {
            if (Neuron.fire(xs[i], w.w(), w.bias()) != ys[i]) {
                return Arrays.toString(xs[i]) + " should give " + ys[i];
            }
        }
        return null;
    }

    @Test
    void trainNeuron() {
        R.task("train_neuron", () -> {
            double[][] two = {{0, 0}, {0, 1}, {1, 0}, {1, 1}};
            double[][] days = {{0, 0, 0}, {1, 0, 0}, {0, 1, 0}, {0, 0, 1}, {1, 1, 0}, {1, 0, 1}, {0, 1, 1}, {1, 1, 1}};
            Object[][] sets = {{"AND", two, new int[] {0, 0, 0, 1}}, {"OR", two, new int[] {0, 1, 1, 1}},
                {"the late-train days", days, new int[] {0, 0, 0, 1, 1, 1, 1, 1}}};
            for (Object[] s : sets) {
                Neuron.Weights w = Neuron.train((double[][]) s[1], (int[]) s[2], 20, 0.1);
                String wrong = w == null ? "train returned null" : mistakes((double[][]) s[1], (int[]) s[2], w);
                if (wrong != null) {
                    R.fail("train_neuron", "After training on " + s[0] + " for 20 epochs the neuron still gets an example wrong: " + wrong
                            + ". For each example: error = answer - fire(...); then add rate * error * input to each weight, and rate * error to the bias.");
                    return;
                }
            }
            // A rule the check makes up: the neuron must learn it from examples alone.
            Random r = new Random(7);
            double[][] xs = new double[40][4];
            int[] ys = new int[40];
            for (int i = 0; i < xs.length; i++) {
                for (int k = 0; k < 4; k++) xs[i][k] = r.nextInt(3);
                ys[i] = 2 * xs[i][0] - xs[i][1] + xs[i][2] - 0.5 * xs[i][3] > 0.75 ? 1 : 0;
            }
            Neuron.Weights w = Neuron.train(xs, ys, 200, 0.1);
            String wrong = mistakes(xs, ys, w);
            if (wrong != null) {
                R.fail("train_neuron", "The neuron learned AND and OR, but not a new rule from 40 examples (200 epochs): " + wrong
                        + ". Make sure every epoch goes through every example, and updates use that example's own inputs.");
                return;
            }
            R.pass("train_neuron", "Your neuron learned AND, OR and a rule nobody told it, from examples only. Rosenblatt's 1958 rule, in a dozen lines.");
        });
    }
}
