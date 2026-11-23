package com.atlas;

import java.util.List;

/** A golden question: a real visitor question, and the card that must be found for it. */
public record Golden(String question, String file) {

    /** Collected from the lobby screen's logs, and checked by a curator. Add every question Atlas got wrong. */
    public static final List<Golden> QUESTIONS = List.of(
            new Golden("Where is the pendulum?", "foucault-pendulum.md"),
            new Golden("Which exhibit shows that the Earth spins?", "foucault-pendulum.md"),
            new Golden("How much is a ticket for a child?", "visitor-information.md"),
            new Golden("Is the museum open on Monday?", "visitor-information.md"),
            new Golden("Is there a lift for my grandmother's wheelchair?", "visitor-information.md"),
            new Golden("When is the black holes show?", "planetarium.md"),
            new Golden("Has India sent anything to Mars?", "mangalyaan.md"),
            new Golden("What did India find on the Moon?", "chandrayaan-3.md"),
            new Golden("Do you have a dinosaur?", "rajasaurus.md"),
            new Golden("Who took the X-ray photos of DNA?", "dna-model.md"),
            new Golden("Why is the picture upside down in the dark room?", "camera-obscura.md"),
            new Golden("Where do the colours of a rainbow come from?", "prism-room.md"),
            new Golden("Can I talk to my friend across the gallery?", "whispering-dishes.md"),
            new Golden("How many bulbs can I light by pedalling?", "bicycle-generator.md"),
            new Golden("Does the museum make its own electricity?", "solar-tree.md"));
}
