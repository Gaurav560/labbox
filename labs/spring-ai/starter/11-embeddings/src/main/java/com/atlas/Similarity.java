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
        // TODO (task cosine_similarity): the dot product of a and b, divided by the length of a times the length of b.
        return 0;
    }
}
