package com.setu.check;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;

import java.util.List;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.context.ApplicationContext;
import org.springframework.http.MediaType;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;

import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingSearchRequest;
import dev.langchain4j.store.embedding.EmbeddingStore;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

@SpringBootTest
@AutoConfigureMockMvc
class Ch30Check {

    static final FakeOpenAi FAKE = new FakeOpenAi();
    static final JsonMapper JSON = JsonMapper.builder().build();

    @DynamicPropertySource
    static void ai(DynamicPropertyRegistry r) {
        r.add("langchain4j.open-ai.chat-model.base-url", FAKE::baseUrl);
        r.add("langchain4j.open-ai.chat-model.api-key", () -> "check-key");
        r.add("langchain4j.open-ai.embedding-model.base-url", FAKE::baseUrl);
        r.add("langchain4j.open-ai.embedding-model.api-key", () -> "check-key");
    }

    @AfterAll
    static void stop() { FAKE.stop(); }

    @Autowired
    ApplicationContext context;

    @Autowired
    MockMvc mvc;

    @Test
    void rulesStore() {
        R.task("rules_store", () -> {
            @SuppressWarnings("unchecked")
            EmbeddingStore<TextSegment> store = context.getBean("rulesStore", EmbeddingStore.class);
            EmbeddingModel model = context.getBean(EmbeddingModel.class);
            var matches = store.search(EmbeddingSearchRequest.builder()
                    .queryEmbedding(model.embed("Can I take my bicycle?").content()).maxResults(3).minScore(0.7).build()).matches();
            if (matches.isEmpty()) {
                R.fail("rules_store", "The rule book store is empty: load the documents with ClassPathDocumentLoader.loadDocuments(\"rules\", new TextDocumentParser()) and ingest them with an EmbeddingStoreIngestor into the store you return.");
                return;
            }
            String file = matches.get(0).embedded().metadata().getString("file_name");
            if (!"luggage.txt".equals(file)) {
                R.fail("rules_store", "A bicycle question should find the luggage rules first.", "luggage.txt", String.valueOf(file));
                return;
            }
            if (matches.get(0).embedded().text().length() > 330) {
                R.fail("rules_store", "Split the documents into small pieces: .documentSplitter(DocumentSplitters.recursive(300, 30)).");
                return;
            }
            R.pass("rules_store", "The rule book is indexed once, at start-up, and the bicycle question finds the luggage rules.");
        });
    }

    @Test
    void answerWithSources() {
        R.task("answer_with_sources", () -> {
            FAKE.reset();
            FAKE.script = b -> FakeOpenAi.Reply.text("Yes, bicycles travel in the guard's van for Rs 60.");
            var res = mvc.perform(post("/chat").contentType(MediaType.APPLICATION_JSON)
                    .content("{\"passenger\": \"meera\", \"message\": \"Can I take my bicycle?\"}")).andReturn().getResponse();
            if (res.getStatus() == 404 || res.getStatus() == 405) {
                R.fail("answer_with_sources", "POST /chat answered " + res.getStatus() + ": add @PostMapping(\"/chat\") with a @RequestBody ChatRequest parameter.", "200", String.valueOf(res.getStatus()));
                return;
            }
            if (res.getStatus() != 200) {
                R.fail("answer_with_sources", "POST /chat answered " + res.getStatus() + ".", "200", String.valueOf(res.getStatus()));
                return;
            }
            JsonNode body = JSON.readTree(res.getContentAsString());
            if (!"Yes, bicycles travel in the guard's van for Rs 60.".equals(body.path("answer").asString())) {
                R.fail("answer_with_sources", "The answer should be result.content(), the model's text.", "Yes, bicycles travel in the guard's van for Rs 60.", res.getContentAsString());
                return;
            }
            List<String> sources = new java.util.ArrayList<>();
            body.path("sources").forEach(s -> sources.add(s.asString()));
            if (!sources.contains("luggage.txt")) {
                R.fail("answer_with_sources", "The sources should list the file each retrieved piece came from: content.textSegment().metadata().getString(\"file_name\").",
                        "[luggage.txt]", sources.toString());
                return;
            }
            if (sources.size() != sources.stream().distinct().count()) {
                R.fail("answer_with_sources", "Each file should appear once: add .distinct().", "[luggage.txt]", sources.toString());
                return;
            }
            String user = String.join(" ", FakeOpenAi.texts(FAKE.chat(-1), "user"));
            if (!user.contains("guard's van")) {
                R.fail("answer_with_sources", "The rule book was not sent to the model with the question. Keep the rulesRetriever bean, and let @AiService wire it.");
                return;
            }
            R.pass("answer_with_sources", "Setu in production: tools, memory, guardrails, a listener and the rule book, and every answer says where it came from.");
        });
    }
}
