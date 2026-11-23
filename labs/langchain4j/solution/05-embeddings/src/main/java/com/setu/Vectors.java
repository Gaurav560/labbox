package com.setu;

/** Embeddings are vectors: lists of numbers. Similar meanings point in similar directions. */
public final class Vectors {

    private Vectors() {
    }

    /** 1 for the same direction, 0 for unrelated, -1 for opposite. */
    public static double cosine(float[] a, float[] b) {
        double dot = 0;
        double lengthA = 0;
        double lengthB = 0;
        for (int i = 0; i < a.length; i++) {
            dot += a[i] * b[i];
            lengthA += a[i] * a[i];
            lengthB += b[i] * b[i];
        }
        return dot / (Math.sqrt(lengthA) * Math.sqrt(lengthB));
    }
}
