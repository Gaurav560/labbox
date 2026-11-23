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

    // TODO (task rule_reply): answer from the rules. Capitals must not matter.
    //   a question with "refund" gets REFUND; with "luggage" or "bag" gets LUGGAGE;
    //   with "pet" or "dog" gets PETS; anything else gets UNKNOWN.
    public static String reply(String question) {
        return UNKNOWN;
    }
}
