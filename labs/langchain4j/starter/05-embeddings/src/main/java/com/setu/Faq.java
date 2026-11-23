package com.setu;

import java.util.LinkedHashMap;
import java.util.Map;

import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.embedding.onnx.bgesmallenv15q.BgeSmallEnV15QuantizedEmbeddingModel;

/** Setu's frequently asked questions, matched by meaning, not by keyword. */
public final class Faq {

    /** A small embedding model that runs inside your program: no network, no cost. 384 numbers per text. */
    static final EmbeddingModel MODEL = new BgeSmallEnV15QuantizedEmbeddingModel();

    static final Map<String, String> ENTRIES = new LinkedHashMap<>();

    static {
        ENTRIES.put("How do I get my money back for a cancelled ticket?",
                "Refunds: the full fare up to 24 hours before departure, half the fare after that.");
        ENTRIES.put("How much baggage can I carry?", "Each passenger may carry 40 kg of luggage free of charge.");
        ENTRIES.put("Can I travel with my cat or dog?", "Small pets travel in the guard's van, with a pet ticket of Rs 120.");
        ENTRIES.put("Is there food on the train?", "The Ghat Express has a pantry car; the other trains stop at Lonavala for 10 minutes.");
        ENTRIES.put("Where do I park my car at Pune station?", "The multi-level parking at Pune station is open 24 hours, Rs 40 for 4 hours.");
    }

    private Faq() {
    }

    /** The embedding (a vector of 384 numbers) of a text. */
    public static float[] embed(String text) {
        return MODEL.embed(text).content().vector();
    }

    // TODO (task closest_question): embed the passenger's question, compare it (Vectors.cosine) with the embedding
    //   of every question in ENTRIES, and return the answer of the most similar one.
    public static String answer(String question) {
        return "Sorry, I don't know that yet.";
    }
}
