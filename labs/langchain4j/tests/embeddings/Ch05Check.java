package com.setu.check;

import org.junit.jupiter.api.Test;

import com.setu.Faq;
import com.setu.Vectors;

class Ch05Check {

    @Test
    void cosine() {
        R.task("cosine", () -> {
            Object[][] cases = {
                {new float[] {1, 0}, new float[] {0, 1}, 0.0}, {new float[] {1, 2, 3}, new float[] {1, 2, 3}, 1.0},
                {new float[] {1, 2}, new float[] {-1, -2}, -1.0}, {new float[] {1, 2}, new float[] {10, 20}, 1.0},
                {new float[] {3, 4}, new float[] {4, 3}, 0.96}};
            for (Object[] c : cases) {
                double got = Vectors.cosine((float[]) c[0], (float[]) c[1]);
                if (Double.isNaN(got) || Math.abs(got - (double) c[2]) > 1e-6) {
                    String hint = (double) c[2] == 1.0 && ((float[]) c[1])[0] == 10
                            ? "A longer vector in the same direction must still give 1: divide by the two lengths."
                            : "Dot product of a and b, divided by (length of a times length of b).";
                    R.fail("cosine", "cosine(" + java.util.Arrays.toString((float[]) c[0]) + ", " + java.util.Arrays.toString((float[]) c[1]) + ") is wrong. " + hint,
                            String.valueOf(c[2]), String.valueOf(got));
                    return;
                }
            }
            R.pass("cosine", "Cosine similarity compares direction, not length: the measure behind every semantic search.");
        });
    }

    @Test
    void closestQuestion() {
        R.task("closest_question", () -> {
            if (Vectors.cosine(new float[] {1, 2}, new float[] {1, 2}) < 0.99) {
                R.fail("closest_question", "Faq.answer compares embeddings with Vectors.cosine, which is not working yet: finish the task before this one (cosine) first.");
                return;
            }
            String[][] cases = {
                {"My trip is cancelled, can I get my money back?", "Refunds"},
                {"How many kilos of suitcases are allowed?", "40 kg"},
                {"Can my kitten come with me?", "Small pets"},
                {"Can I buy lunch on board?", "pantry car"},
                {"Where can I leave my car while I travel?", "parking"}};
            for (String[] c : cases) {
                String got = Faq.answer(c[0]);
                if (got == null || !got.contains(c[1])) {
                    R.fail("closest_question", "Faq.answer(\"" + c[0] + "\") picked the wrong entry. Embed the question once, compare it with the embedding of every ENTRIES question using Vectors.cosine, and return the answer of the highest score.",
                            "the answer containing \"" + c[1] + "\"", String.valueOf(got));
                    return;
                }
            }
            R.pass("closest_question", "No keyword matched \"suitcases\" or \"kitten\", yet Setu found the right answer: that is meaning, as numbers.");
        });
    }
}
