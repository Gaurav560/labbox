package com.setu;

import java.util.Locale;

/** Setu's first help desk: rules written by hand, the oldest kind of AI. */
public final class Rules {

    static final String REFUND = "Refunds: the full fare up to 24 hours before departure, half the fare after that.";
    static final String LUGGAGE = "Each passenger may carry 40 kg of luggage free of charge.";
    static final String PETS = "Small pets travel in the guard's van, with a pet ticket of Rs 120.";
    static final String UNKNOWN = "Sorry, I don't know that yet. Please ask at the station office.";

    private Rules() {
    }

    /** Answers from the rules: the first rule whose keyword appears in the question wins. */
    public static String reply(String question) {
        String q = question.toLowerCase(Locale.ROOT);
        if (q.contains("refund")) {
            return REFUND;
        }
        if (q.contains("luggage") || q.contains("bag")) {
            return LUGGAGE;
        }
        if (q.contains("pet") || q.contains("dog")) {
            return PETS;
        }
        return UNKNOWN;
    }
}
