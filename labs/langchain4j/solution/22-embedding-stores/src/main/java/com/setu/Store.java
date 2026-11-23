package com.setu;

import java.util.ArrayList;
import java.util.List;

import dev.langchain4j.data.document.Metadata;
import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.openai.OpenAiEmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingMatch;
import dev.langchain4j.store.embedding.EmbeddingSearchRequest;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.inmemory.InMemoryEmbeddingStore;

/** An embedding store: vectors, with the text and metadata they came from, searchable by meaning. */
public final class Store {

    private Store() {
    }

    /** OpenAI's text-embedding-3-small behind the gateway (alias ai-embed): 1,536 numbers per text. */
    public static EmbeddingModel embeddingModel(String baseUrl, String apiKey) {
        return OpenAiEmbeddingModel.builder()
                .baseUrl(baseUrl)
                .apiKey(apiKey)
                .modelName("ai-embed")
                .build();
    }

    /** Embed each card once and keep the vector with its text and metadata. */
    public static EmbeddingStore<TextSegment> load(EmbeddingModel model, List<Cards.Card> cards) {
        EmbeddingStore<TextSegment> store = new InMemoryEmbeddingStore<>();
        for (Cards.Card card : cards) {
            TextSegment segment = TextSegment.from(card.text(), Metadata.from("title", card.title()).put("type", card.type()));
            Embedding embedding = model.embed(segment).content();
            store.add(embedding, segment);
        }
        return store;
    }

    /** The titles of the closest cards, best first, scoring at least 0.7. */
    public static List<String> search(EmbeddingStore<TextSegment> store, EmbeddingModel model, String question, int max) {
        EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
                .queryEmbedding(model.embed(question).content())
                .maxResults(max)
                .minScore(0.7)
                .build();
        List<String> titles = new ArrayList<>();
        for (EmbeddingMatch<TextSegment> match : store.search(request).matches()) {
            titles.add(match.embedded().metadata().getString("title"));
        }
        return titles;
    }
}
