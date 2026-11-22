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

/** Chapter 14: retrieval-augmented generation, with sources. */
@SpringBootTest
@AutoConfigureMockMvc
class Ch14Check {
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

    @Test
    void ragAnswer() {
        R.task("rag_answer", () -> {
            AI.reset();
            AI.script = b -> FakeOpenAi.Reply.text("The wire is 15 metres long.");
            call("/ask", "q", "How long is the wire of the Foucault pendulum?");
            String user = String.join(" ", FakeOpenAi.texts(AI.chat(-1), "user"));
            if (!user.contains("15 metre steel wire")) {
                R.fail("rag_answer", "the question reached the model without the pendulum card. Add a QuestionAnswerAdvisor built on the vector store to the ChatClient.", "the question plus the pendulum card's text", user.length() > 160 ? user.substring(0, 160) + "..." : user);
                return;
            }
            if (user.contains("Rajasaurus") || user.contains("solar panels")) {
                R.fail("rag_answer", "unrelated cards came along with the pendulum card. Search for the 3 closest, with similarityThreshold(0.35).");
                return;
            }
            R.pass("rag_answer", "The pendulum card travelled with the question, and nothing unrelated: Atlas now answers from the museum's own facts.");
        });
    }

    @Test
    void citeSources() {
        R.task("cite_sources", () -> {
            AI.reset();
            AI.script = b -> FakeOpenAi.Reply.text("The wire is 15 metres long.");
            JsonNode r = JSON.readTree(call("/ask/sourced", "q", "How long is the wire of the Foucault pendulum?"));
            if (!"The wire is 15 metres long.".equals(r.path("answer").asString(""))) {
                R.fail("cite_sources", "the answer field should hold the model's answer.", "The wire is 15 metres long.", r.path("answer").asString(""));
                return;
            }
            var sources = r.path("sources").toString();
            if (!sources.contains("foucault-pendulum.md")) {
                R.fail("cite_sources", "the sources should list the cards the advisor retrieved, read from response.context().get(QuestionAnswerAdvisor.RETRIEVED_DOCUMENTS).", "[\"foucault-pendulum.md\"]", sources);
                return;
            }
            R.pass("cite_sources", "An answer with its source, foucault-pendulum.md: a visitor (or a curator) can check where it came from.");
        });
    }
}
