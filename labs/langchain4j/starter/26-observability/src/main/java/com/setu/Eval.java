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

    // TODO (task golden_eval): ask the assistant every golden question and return the share (0.0 to 1.0) of answers
    //   that contain its mustContain text, ignoring capitals (lower-case both with Locale.ROOT).
    public static double passRate(Assistant assistant, List<Golden> golden) {
        return 0;
    }
}
