package com.setu;

/** Chapter 6: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) {
        // A model has scored four possible next words after "The Ghat Express is running ...".
        String[] next = {"late", "early", "smoothly", "backwards"};
        double[] scores = {4.0, 2.5, 2.0, -1.0};
        for (double temperature : new double[] {0.2, 1.0, 2.0}) {
            double[] p = Attention.softmax(scores, temperature);
            StringBuilder line = new StringBuilder("temperature " + temperature + ": ");
            for (int i = 0; i < next.length; i++) {
                line.append(String.format("%s %.2f  ", next[i], p[i]));
            }
            System.out.println(line);
        }

        // "The train left the station because it was on time": what does "it" attend to?
        String[] words = {"train", "station", "it"};
        double[][] keys = {{1.0, 0.9, 0.1}, {0.1, 0.2, 1.0}, {0.8, 0.7, 0.3}};
        double[] query = {1.0, 1.0, 0.0};   // the query of "it": looking for something that moves on a schedule
        double[] w = Attention.weights(query, keys);
        for (int i = 0; i < words.length; i++) {
            System.out.printf("'it' attends to %-8s %.2f%n", words[i], w[i]);
        }
    }
}
