package com.setu;

import java.util.List;

/** The railway's help cards: short answers, each with a title and a type. */
public final class Cards {

    public record Card(String title, String type, String text) {
    }

    private Cards() {
    }

    public static final List<Card> ALL = List.of(
            new Card("Refunds", "rule", "Cancel up to 24 hours before departure for a full refund; after that, half the fare. Refunds reach your account in 5 working days."),
            new Card("Luggage", "rule", "Each passenger may carry 40 kg of luggage free. Bicycles travel in the guard's van for Rs 60."),
            new Card("Pets", "rule", "Small pets travel in the guard's van with a pet ticket of Rs 120. Guide dogs travel with their owner, free."),
            new Card("Monsoon", "service", "In heavy rain, trains on the ghat may stop for safety checks. Delays are announced on platforms and by SMS."),
            new Card("Lost property", "service", "Items found on trains are kept at Pune station, platform 1, for 30 days. Bring a photo ID."),
            new Card("Accessibility", "service", "The Ghat Express has four wheelchair spaces. Ramps are available at every station on request."));
}
