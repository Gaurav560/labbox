package com.setu;

import java.util.List;

import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingMatch;
import dev.langchain4j.store.embedding.EmbeddingSearchRequest;
import dev.langchain4j.store.embedding.EmbeddingStore;

/** Chapter 22: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) {
        EmbeddingModel model = Store.embeddingModel(System.getenv("OPENAI_BASE_URL"), System.getenv("OPENAI_API_KEY"));
        System.out.println("dimensions: " + model.dimension());
        EmbeddingStore<TextSegment> store = Store.load(model, Cards.ALL);
        for (String q : new String[] {"Can I take my bicycle?", "My train is stuck because of rain",
                "I left my bag on the train", "What is the capital of France?"}) {
            System.out.println(q + " -> " + Store.search(store, model, q, 2));
        }
        // The scores behind those answers, with no threshold: why minScore matters.
        System.out.println();
        for (String q : new String[] {"Can I take my bicycle?", "What is the capital of France?"}) {
            EmbeddingSearchRequest top3 = EmbeddingSearchRequest.builder()
                    .queryEmbedding(model.embed(q).content()).maxResults(3).build();
            StringBuilder line = new StringBuilder(q);
            for (EmbeddingMatch<TextSegment> m : store.search(top3).matches()) {
                line.append(String.format("  %.3f %s", m.score(), m.embedded().metadata().getString("title")));
            }
            System.out.println(line);
        }
    }
}
