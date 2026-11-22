package com.atlas;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.asyncDispatch;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;

@SpringBootTest
@AutoConfigureMockMvc
class ProbeTest {
    static final FakeOpenAi AI = new FakeOpenAi();

    @DynamicPropertySource
    static void props(DynamicPropertyRegistry r) {
        r.add("spring.ai.openai.base-url", AI::baseUrl);
        r.add("spring.ai.openai.api-key", () -> "test-key");
    }

    @AfterAll
    static void stop() { AI.stop(); }

    @Autowired
    MockMvc mvc;

    String get1(String url) throws Exception {
        return mvc.perform(get(url)).andReturn().getResponse().getContentAsString();
    }

    @Test
    void all() throws Exception {
        System.out.println("ASK: " + get1("/ask?q=When is the planetarium show?"));
        System.out.println("REQ ASK: " + AI.lastChat());
        System.out.println("USAGE: " + get1("/usage?q=hi"));
        AI.script = b -> FakeOpenAi.Reply.text("{\"title\":\"Space\",\"stops\":[{\"gallery\":\"Planetarium\",\"minutes\":30}]}");
        System.out.println("PLAN: " + get1("/plan"));
        System.out.println("REQ PLAN: " + AI.lastChat());
        AI.script = b -> FakeOpenAi.Reply.text("The show starts at four.");
        MvcResult async = mvc.perform(get("/stream?q=show")).andReturn();
        System.out.println("STREAM: " + mvc.perform(asyncDispatch(async)).andReturn().getResponse().getContentAsString());
        System.out.println("REQ STREAM: " + AI.lastChat());
        AI.script = b -> b.contains("\"role\":\"tool\"") ? FakeOpenAi.Reply.text("On Monday we are closed.") : FakeOpenAi.Reply.tool("openingHours", "{\"day\":\"MONDAY\"}");
        System.out.println("HOURS: " + get1("/hours?q=Open on Monday?"));
        System.out.println("REQ HOURS(last): " + AI.lastChat());
        System.out.println("EMBED: " + get1("/embed?q=pendulum"));
        AI.script = b -> FakeOpenAi.Reply.text("Gallery 2.");
        System.out.println("RAG: " + get1("/rag?q=Where is the pendulum?"));
        System.out.println("REQ RAG: " + AI.lastChat());
        System.out.println("CHAT1: " + get1("/chat?id=a&q=My name is Ria"));
        System.out.println("CHAT2: " + get1("/chat?id=a&q=What is my name?"));
        System.out.println("REQ CHAT2: " + AI.lastChat());
    }
}
