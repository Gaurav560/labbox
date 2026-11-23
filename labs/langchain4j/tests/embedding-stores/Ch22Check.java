package com.setu.check;

import java.util.List;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;

import com.setu.Cards;
import com.setu.Store;

import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.openai.OpenAiEmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingSearchRequest;
import dev.langchain4j.store.embedding.EmbeddingStore;

class Ch22Check {

    static final FakeOpenAi FAKE = new FakeOpenAi();

    @AfterAll
    static void stop() { FAKE.stop(); }

    static EmbeddingModel model() {
        return OpenAiEmbeddingModel.builder().baseUrl(FAKE.baseUrl()).apiKey("k").modelName("ai-embed").build();
    }

    @Test
    void storeCards() {
        R.task("store_cards", () -> {
            EmbeddingModel model = model();
            EmbeddingStore<TextSegment> store = Store.load(model, Cards.ALL);
            var all = store.search(EmbeddingSearchRequest.builder().queryEmbedding(model.embed("refund").content()).maxResults(20).minScore(0.0).build()).matches();
            if (all.size() != Cards.ALL.size()) {
                R.fail("store_cards", "The store holds " + all.size() + " entries; it should hold one per card. For each card, embed a TextSegment and store.add(embedding, segment).",
                        String.valueOf(Cards.ALL.size()), String.valueOf(all.size()));
                return;
            }
            TextSegment top = all.get(0).embedded();
            if (top == null || !"Refunds".equals(top.metadata().getString("title")) || !"rule".equals(top.metadata().getString("type"))) {
                R.fail("store_cards", "Keep the card's title and type as metadata: TextSegment.from(card.text(), Metadata.from(\"title\", card.title()).put(\"type\", card.type())), and add the segment with its embedding.",
                        "metadata title=Refunds, type=rule", top == null ? "no segment stored" : top.metadata().toMap().toString());
                return;
            }
            R.pass("store_cards", "Six cards, each stored as a vector with its text and metadata: an embedding store, in memory.");
        });
    }

    @Test
    void searchStore() {
        R.task("search_store", () -> {
            EmbeddingModel model = model();
            EmbeddingStore<TextSegment> store = new dev.langchain4j.store.embedding.inmemory.InMemoryEmbeddingStore<>();
            for (Cards.Card c : Cards.ALL) {
                TextSegment s = TextSegment.from(c.text(), dev.langchain4j.data.document.Metadata.from("title", c.title()).put("type", c.type()));
                store.add(model.embed(s).content(), s);
            }
            List<String> got = Store.search(store, model, "Can I take my bicycle?", 3);
            if (!List.of("Luggage").equals(got)) {
                String hint = got != null && got.size() > 1 && got.get(0).equals("Luggage")
                        ? "Luggage is first, but weaker matches came too: add minScore(0.7) to the request."
                        : "Embed the question, search with EmbeddingSearchRequest (queryEmbedding, maxResults(max), minScore(0.7)), and return each match's \"title\" metadata.";
                R.fail("search_store", "search(\"Can I take my bicycle?\") should find only the Luggage card. " + hint, "[Luggage]", String.valueOf(got));
                return;
            }
            if (!List.of("Monsoon").equals(Store.search(store, model, "Heavy rain on the ghat", 1))) {
                R.fail("search_store", "search(\"Heavy rain on the ghat\", 1) should find the Monsoon card.", "[Monsoon]", String.valueOf(Store.search(store, model, "Heavy rain on the ghat", 1)));
                return;
            }
            R.pass("search_store", "Search by meaning with a sensible threshold: the right card, and nothing that merely scored above zero.");
        });
    }
}
