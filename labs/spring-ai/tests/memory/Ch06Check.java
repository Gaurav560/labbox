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

/** Chapter 6: session memory per visitor, and a compaction window on it. */
@SpringBootTest
@AutoConfigureMockMvc
class Ch06Check {
    static final FakeOpenAi AI = new FakeOpenAi();

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

    String chat(String visitor, String q) throws Exception {
        return mvc.perform(get("/chat").param("visitor", visitor).param("q", q)).andReturn().getResponse().getContentAsString();
    }

    /** Every user and assistant text in a request, in order. */
    static java.util.List<String> turns(JsonNode req) {
        java.util.List<String> out = new java.util.ArrayList<>();
        for (JsonNode m : req.path("messages")) {
            String role = m.path("role").asString();
            if (role.equals("user") || role.equals("assistant")) out.add(role + ": " + m.path("content").asString(""));
        }
        return out;
    }

    @Test
    void chatMemory() {
        R.task("session_memory", () -> {
            AI.reset();
            AI.script = b -> FakeOpenAi.Reply.text(b.contains("My name is Ria") && !b.contains("What is my name") ? "Nice to meet you, Ria." : "Your name is Ria.");
            chat("ria", "My name is Ria.");
            chat("ria", "What is my name?");
            var t = turns(AI.chat(-1));
            if (!t.contains("user: My name is Ria.") || !t.contains("assistant: Nice to meet you, Ria.")) {
                R.fail("session_memory", "the second message of a visitor did not carry the first one. Add the session advisors to the ChatClient (SessionAdvisors.builder(sessions).build()), and run each call in the visitor's session.", "the earlier question and answer, then the new question", t.toString());
                return;
            }
            AI.script = b -> FakeOpenAi.Reply.text("I do not know your name yet.");
            chat("sam", "What is my name?");
            if (AI.chat(-1).toString().contains("Ria")) {
                R.fail("session_memory", "Sam's request contained Ria's conversation: every visitor needs their own session. Pass the visitor id with .advisors(SessionAdvisors.session(visitor)).");
                return;
            }
            R.pass("session_memory", "Ria's second question carried her first one, and Sam's carried nothing of hers: one session per visitor.");
        });
    }

    @Test
    void memoryWindow() {
        R.task("memory_window", () -> {
            AI.reset();
            AI.script = b -> FakeOpenAi.Reply.text("Noted.");
            for (int i = 1; i <= 9; i++) chat("long", "Question number " + i);
            chat("long", "Question number 10");
            var t = turns(AI.chat(-1));
            boolean hasRecent = t.contains("user: Question number 9");
            boolean hasOld = t.contains("user: Question number 1");
            if (!hasRecent) {
                R.fail("memory_window", "the conversation is not remembered yet, so there is no window to check. Do the session_memory task first.", "earlier questions in the request", t.toString());
                return;
            }
            if (hasOld || t.size() > 9) {
                R.fail("memory_window", "after ten questions, the request still carries the oldest ones. Give the session advisors a compaction: a TurnCountTrigger of 8 and a window of the last 4 turns.", "the last 4 turns, plus the new question", t.size() + " messages, starting with " + t.get(0));
                return;
            }
            R.pass("memory_window", "After ten questions, only the last four turns travel with the request (" + t.size() + " messages): a long conversation stops getting dearer.");
        });
    }
}
