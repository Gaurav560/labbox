package com.setu;

import java.util.Arrays;

/** Chapter 2: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) {
        // Will the 7:15 Ghat Express be late? Inputs: heavy rain (1 or 0), a holiday rush (1 or 0), track work (1 or 0).
        double[][] days = {{0, 0, 0}, {1, 0, 0}, {0, 1, 0}, {0, 0, 1}, {1, 1, 0}, {1, 0, 1}, {0, 1, 1}, {1, 1, 1}};
        int[] late = {0, 0, 0, 1, 1, 1, 1, 1};
        Neuron.Weights trained = Neuron.train(days, late, 20, 0.1);
        System.out.println("weights " + Arrays.toString(trained.w()) + ", bias " + trained.bias());
        for (int i = 0; i < days.length; i++) {
            System.out.println(Arrays.toString(days[i]) + " -> predicted " + Neuron.fire(days[i], trained.w(), trained.bias())
                    + ", actual " + late[i]);
        }
    }
}
