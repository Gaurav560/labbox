package com.atlas.check;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.VectorStore;

/** Chapter 12: cards in a vector store, and search with topK and a threshold. */
@SpringBootTest
@AutoConfigureMockMvc
class Ch12Check {
    static final FakeOpenAi AI = new FakeOpenAi();
    static final JsonMapper JSON = JsonMapper.builder().build();

    @DynamicPropertySource
    static void ai(DynamicPropertyRegistry r) {
        r.add("spring.ai.openai.base-url", AI::baseUrl);
        r.add("spring.ai.openai.api-key", () -> "check-key");
    }

    @AfterAll
    static void stop() {
        AI.stop();
    }

    @Autowired
    MockMvc mvc;

    String call(String path, String... params) throws Exception {
        var req = get(path);
        for (int i = 0; i + 1 < params.length; i += 2) req = req.param(params[i], params[i + 1]);
        return mvc.perform(req).andReturn().getResponse().getContentAsString();
    }

    @Autowired
    VectorStore store;

    @Test
    void addDocuments() {
        R.task("add_documents", () -> {
            var all = store.similaritySearch(SearchRequest.builder().query("gallery").topK(100).similarityThresholdAll().build());
            if (all.isEmpty()) {
                R.fail("add_documents", "the vector store is empty after start-up. In CardLoader.run, add the documents to the store.");
                return;
            }
            long withFile = all.stream().filter(d -> String.valueOf(d.getMetadata().get("file")).endsWith(".md")).count();
            if (all.size() != 12 || withFile != 12) {
                R.fail("add_documents", "the store should hold the 12 exhibit cards, each with its file name.", "12 cards", all.size() + " documents, " + withFile + " with a file");
                return;
            }
            R.pass("add_documents", "12 cards in the store, each embedded as it was added, each knowing its file.");
        });
    }

    @Test
    void searchCards() {
        R.task("search_cards", () -> {
            JsonNode hits = JSON.readTree(call("/search", "q", "Where is the pendulum?", "k", "2"));
            if (!hits.isArray() || hits.isEmpty()) {
                R.fail("search_cards", "GET /search found nothing. Ask the store with store.similaritySearch(SearchRequest.builder()...).", "the pendulum card first", hits.toString());
                return;
            }
            if (!"foucault-pendulum.md".equals(hits.get(0).path("file").asString(""))) {
                R.fail("search_cards", "the best match should come first.", "foucault-pendulum.md", hits.get(0).path("file").asString(""));
                return;
            }
            for (JsonNode h : hits) {
                if (h.path("score").asDouble() < 0.5) {
                    R.fail("search_cards", "a weak match came back (score " + String.format("%.2f", h.path("score").asDouble()) + "). Set similarityThreshold(0.5) so unrelated cards are left out.");
                    return;
                }
            }
            if (hits.size() > 2) {
                R.fail("search_cards", "k=2 asked for at most two cards. Use topK(k).", "at most 2", hits.size() + " cards");
                return;
            }
            R.pass("search_cards", "The pendulum card came first, with a score of " + String.format("%.2f", hits.get(0).path("score").asDouble()) + ", and nothing weak came with it.");
        });
    }
}
