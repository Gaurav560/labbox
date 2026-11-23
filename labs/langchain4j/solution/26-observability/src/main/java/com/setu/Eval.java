package com.setu;

import java.util.List;
import java.util.Locale;

/** A golden set: real questions with a word the right answer must contain. */
public final class Eval {

    public record Golden(String question, String mustContain) {
    }

    public static final List<Golden> GOLDEN = List.of(
            new Golden("When does the Ghat Express leave Pune?", "07:15"),
            new Golden("How much is a ticket from Pune to Ratnagiri?", "420"),
            new Golden("Does the Konkan Breeze run on Tuesdays?", "not"),
            new Golden("When does the Monsoon Mail reach Karjat?", "18:40"),
            new Golden("Do small children need a ticket?", "free"),
            new Golden("Is there wifi on the Ghat Express?", "don't know"));

    private Eval() {
    }

    /** The share of golden questions answered with the expected text. */
    public static double passRate(Assistant assistant, List<Golden> golden) {
        int passed = 0;
        for (Golden g : golden) {
            String answer = assistant.chat(g.question()).toLowerCase(Locale.ROOT);
            if (answer.contains(g.mustContain().toLowerCase(Locale.ROOT))) {
                passed++;
            } else {
                System.out.println("  MISSED: " + g.question() + " -> " + answer);
            }
        }
        return (double) passed / golden.size();
    }
}
