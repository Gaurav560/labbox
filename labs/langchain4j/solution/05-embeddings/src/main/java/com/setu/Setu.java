package com.setu;

import java.util.Arrays;

/** Chapter 5: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) {
        float[] v = Faq.embed("refund");
        System.out.println("'refund' is " + v.length + " numbers, starting " + Arrays.toString(Arrays.copyOf(v, 5)));

        String[][] pairs = {{"refund", "money back"}, {"refund", "luggage"}, {"dog", "puppy"}, {"dog", "platform"}};
        for (String[] p : pairs) {
            System.out.printf("%-8s ~ %-10s %.3f%n", p[0], p[1], Vectors.cosine(Faq.embed(p[0]), Faq.embed(p[1])));
        }

        for (String q : new String[] {"My trip is cancelled, can I get a refund?", "How heavy can my suitcase be?",
                "Can my puppy come along?"}) {
            System.out.println(q + "\n  -> " + Faq.answer(q));
        }
    }
}
