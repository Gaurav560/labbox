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

import com.setu.SetuAssistant;

import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

@SpringBootTest
@AutoConfigureMockMvc
class Ch18Check {

    static final FakeOpenAi FAKE = new FakeOpenAi();
    static final JsonMapper JSON = JsonMapper.builder().build();

    @DynamicPropertySource
    static void ai(DynamicPropertyRegistry r) {
        r.add("langchain4j.open-ai.chat-model.base-url", FAKE::baseUrl);
        r.add("langchain4j.open-ai.chat-model.api-key", () -> "check-key");
    }

    @AfterAll
    static void stop() { FAKE.stop(); }

    @Autowired
    ApplicationContext context;

    @Autowired
    MockMvc mvc;

    @Test
    void aiServiceBean() {
        R.task("ai_service_bean", () -> {
            SetuAssistant setu = context.getBean(SetuAssistant.class);
            FAKE.reset();
            setu.chat("meera", "Hello");
            if (FakeOpenAi.texts(FAKE.chat(-1), "system").isEmpty()) {
                R.fail("ai_service_bean", "The bean exists but sent no system message: keep @SystemMessage(fromResource = \"setu-system.txt\") on chat(...).");
                return;
            }
            R.pass("ai_service_bean", "@AiService: the starter implemented the interface, wired the model and the memory, and made it a bean.");
        });
    }

    @Test
    void chatEndpoint() {
        R.task("chat_endpoint", () -> {
            FAKE.reset();
            FAKE.script = b -> FakeOpenAi.Reply.text("You asked about the Konkan Breeze.");
            var res = mvc.perform(post("/chat").contentType(MediaType.APPLICATION_JSON)
                    .content("{\"passenger\": \"meera\", \"message\": \"What did I ask?\"}")).andReturn().getResponse();
            if (res.getStatus() == 404 || res.getStatus() == 405) {
                R.fail("chat_endpoint", "POST /chat answered " + res.getStatus() + ": there is no method for it yet. Add @PostMapping(\"/chat\") with a @RequestBody ChatRequest parameter.", "200", String.valueOf(res.getStatus()));
                return;
            }
            if (res.getStatus() != 200) {
                R.fail("chat_endpoint", "POST /chat answered " + res.getStatus() + ".", "200", String.valueOf(res.getStatus()));
                return;
            }
            JsonNode body = JSON.readTree(res.getContentAsString());
            if (!"meera".equals(body.path("passenger").asString()) || !"You asked about the Konkan Breeze.".equals(body.path("answer").asString())) {
                R.fail("chat_endpoint", "Return new ChatReply(request.passenger(), the answer from setu.chat(passenger, message)).",
                        "{\"passenger\":\"meera\",\"answer\":\"You asked about the Konkan Breeze.\"}", res.getContentAsString());
                return;
            }
            if (FAKE.chatRequests.isEmpty() || !FakeOpenAi.texts(FAKE.chat(-1), "user").contains("What did I ask?")) {
                R.fail("chat_endpoint", "The endpoint should pass the message to setu.chat(passenger, message).");
                return;
            }
            R.pass("chat_endpoint", "Setu is a web API: JSON in, JSON out, a conversation per passenger.");
        });
    }
}
