package com.setu;

/** One artificial neuron: inputs times weights, plus a bias; it fires (1) when the sum is above zero. */
public final class Neuron {

    /** What training produces: one weight per input, and the bias. */
    public record Weights(double[] w, double bias) {
    }

    private Neuron() {
    }

    // TODO (task neuron_fire): multiply each input by its weight, add them up, add the bias.
    //   Return 1 if the total is greater than 0, otherwise 0.
    public static int fire(double[] inputs, double[] weights, double bias) {
        return 0;
    }

    // TODO (task train_neuron): the perceptron rule. Start with every weight and the bias at 0. For each epoch, for
    //   each example x with answer y: guess = fire(x, w, bias); error = y - guess;
    //   then w[i] += rate * error * x[i] for every input, and bias += rate * error. Return the weights.
    public static Weights train(double[][] xs, int[] ys, int epochs, double rate) {
        return new Weights(new double[xs[0].length], 0);
    }
}
