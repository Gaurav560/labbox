package com.setu;

/** One artificial neuron: inputs times weights, plus a bias; it fires (1) when the sum is above zero. */
public final class Neuron {

    /** What training produces: one weight per input, and the bias. */
    public record Weights(double[] w, double bias) {
    }

    private Neuron() {
    }

    /** 1 when inputs times weights, plus the bias, is above zero; otherwise 0. */
    public static int fire(double[] inputs, double[] weights, double bias) {
        double sum = bias;
        for (int i = 0; i < inputs.length; i++) {
            sum += inputs[i] * weights[i];
        }
        return sum > 0 ? 1 : 0;
    }

    /** Rosenblatt's perceptron rule: nudge the weights towards every example the neuron gets wrong. */
    public static Weights train(double[][] xs, int[] ys, int epochs, double rate) {
        double[] w = new double[xs[0].length];
        double bias = 0;
        for (int epoch = 0; epoch < epochs; epoch++) {
            for (int n = 0; n < xs.length; n++) {
                int error = ys[n] - fire(xs[n], w, bias);
                for (int i = 0; i < w.length; i++) {
                    w[i] += rate * error * xs[n][i];
                }
                bias += rate * error;
            }
        }
        return new Weights(w, bias);
    }
}
