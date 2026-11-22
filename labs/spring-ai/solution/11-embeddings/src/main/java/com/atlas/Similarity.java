package com.atlas;

/** How alike two embeddings are. */
public final class Similarity {

    private Similarity() {
    }

    /**
     * The cosine similarity of two vectors of the same length: 1 when they point the same way, 0 when they have
     * nothing in common, -1 when they point in opposite directions.
     */
    public static double cosine(float[] a, float[] b) {
        double dot = 0, lengthA = 0, lengthB = 0;
        for (int i = 0; i < a.length; i++) {
            dot += a[i] * b[i];
            lengthA += a[i] * a[i];
            lengthB += b[i] * b[i];
        }
        return dot / (Math.sqrt(lengthA) * Math.sqrt(lengthB));
    }
}
