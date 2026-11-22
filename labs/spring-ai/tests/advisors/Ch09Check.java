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

/** Chapter 9: two advisors of the learner's own. */
@SpringBootTest
@AutoConfigureMockMvc
class Ch09Check {
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

    String call(String url) throws Exception {
        return mvc.perform(get(url)).andReturn().getResponse().getContentAsString();
    }

    @Test
    void usageAdvisor() {
        R.task("usage_advisor", () -> {
            AI.reset();
            JsonNode before = JSON.readTree(call("/meter"));
            call("/ask?q=Hello");
            call("/ask?q=What%20is%20a%20comet%3F");
            JsonNode after = JSON.readTree(call("/meter"));
            if (AI.chatRequests.size() != 2) {
                R.fail("usage_advisor", "the two questions did not both reach the model. An advisor must pass the request on with chain.nextCall(request) and return what comes back.", "2 model calls", AI.chatRequests.size() + " model calls");
                return;
            }
            long calls = after.path("calls").asLong() - before.path("calls").asLong();
            long tokens = after.path("tokens").asLong() - before.path("tokens").asLong();
            if (calls != 2 || tokens != 100) {
                R.fail("usage_advisor", "the meter should count each call and add its total tokens (each pretend answer used 50).", "2 calls, 100 tokens", calls + " calls, " + tokens + " tokens");
                return;
            }
            R.pass("usage_advisor", "Two calls, 100 tokens, counted by one advisor around every call: no controller had to change.");
        });
    }

    @Test
    void languageAdvisor() {
        R.task("language_advisor", () -> {
            AI.reset();
            call("/ask?q=What%20is%20a%20comet%3F&lang=Marathi");
            String withLang = String.join(" ", FakeOpenAi.texts(AI.chat(-1), "system"));
            if (!withLang.contains("Answer in Marathi")) {
                R.fail("language_advisor", "with lang=Marathi the system message should end with \"Answer in Marathi.\". In before(), read request.context(), and change the prompt with request.mutate().", "... Answer in Marathi.", withLang.length() > 160 ? "..." + withLang.substring(withLang.length() - 160) : withLang);
                return;
            }
            if (!withLang.contains("Atlas")) {
                R.fail("language_advisor", "the language was added, but Atlas's own system prompt was lost. Add to the system message; do not replace it.");
                return;
            }
            call("/ask?q=What%20is%20a%20comet%3F");
            String without = String.join(" ", FakeOpenAi.texts(AI.chat(-1), "system"));
            if (without.contains("Answer in Marathi")) {
                R.fail("language_advisor", "without a lang parameter, the system message should stay as it was.");
                return;
            }
            R.pass("language_advisor", "With lang=Marathi the system prompt gained one line; without it, nothing changed. An advisor that edits requests, for every endpoint at once.");
        });
    }
}
