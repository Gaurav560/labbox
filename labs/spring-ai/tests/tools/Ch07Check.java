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

/** Chapter 7: tools the model can call. */
@SpringBootTest
@AutoConfigureMockMvc
class Ch07Check {
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

    String ask(String q) throws Exception {
        return mvc.perform(get("/ask").param("q", q)).andReturn().getResponse().getContentAsString();
    }

    /** The fake model calls one tool if the request offers it, then answers with what the tool returned. */
    static void callTool(String name, String args) {
        AI.script = b -> {
            if (b.contains("\"role\":\"tool\"")) return FakeOpenAi.Reply.text("Here is what I found.");
            if (b.contains("\"name\":\"" + name + "\"")) return FakeOpenAi.Reply.tool(name, args);
            return FakeOpenAi.Reply.text("I do not know.");
        };
    }

    static String toolResult() {
        var r = FakeOpenAi.texts(AI.chat(-1), "tool");
        return r.isEmpty() ? "" : r.get(r.size() - 1);
    }

    static JsonNode tool(JsonNode req, String name) {
        for (JsonNode t : req.path("tools")) if (name.equals(t.path("function").path("name").asString())) return t.path("function");
        return null;
    }

    @Test
    void openingHoursTool() {
        R.task("opening_hours_tool", () -> {
            AI.reset();
            callTool("openingHours", "{\"date\":\"2026-11-30\"}");
            ask("Is the museum open on 30 November?");
            if (AI.chatRequests.isEmpty()) {
                R.fail("opening_hours_tool", "GET /ask never called the model.");
                return;
            }
            JsonNode first = AI.chat(0);
            var names = FakeOpenAi.tools(first);
            if (!names.contains("openingHours")) {
                R.fail("opening_hours_tool", names.isEmpty()
                        ? "the request offered the model no tools. Write the openingHours method with @Tool in MuseumTools, and add .tools(tools) to the prompt in AskController."
                        : "the tools are offered, but none is called openingHours.", "openingHours", names.toString());
                return;
            }
            JsonNode fn = tool(first, "openingHours");
            if (fn.path("description").asString("").isBlank() || !fn.path("parameters").path("properties").has("date")) {
                R.fail("opening_hours_tool", "the model needs a description of the tool and a parameter called date, to know when and how to use it.");
                return;
            }
            String monday = toolResult();
            if (AI.chatRequests.size() < 2 || !monday.toLowerCase().contains("closed")) {
                R.fail("opening_hours_tool", "the model asked for openingHours(2026-11-30), a Monday; the answer sent back should say the museum is closed.", "Closed ...", monday);
                return;
            }
            AI.reset();
            callTool("openingHours", "{\"date\":\"2026-12-01\"}");
            ask("Is the museum open on 1 December?");
            String tuesday = toolResult();
            if (!tuesday.contains("10:00") || !tuesday.contains("18:00")) {
                R.fail("opening_hours_tool", "on a Tuesday the tool should give the opening hours.", "Open ... 10:00 to 18:00 ...", tuesday);
                return;
            }
            R.pass("opening_hours_tool", "The model asked for openingHours, Spring AI ran your method, and the real hours went back to the model: no more invented hours.");
        });
    }

    @Test
    void showTimesTool() {
        R.task("show_times_tool", () -> {
            AI.reset();
            callTool("planetariumShows", "{\"date\":\"2026-11-28\"}");
            ask("Are there seats for the planetarium on Saturday 28 November?");
            if (AI.chatRequests.isEmpty() || !FakeOpenAi.tools(AI.chat(0)).contains("planetariumShows")) {
                R.fail("show_times_tool", "the request does not offer a tool called planetariumShows yet.", "planetariumShows", AI.chatRequests.isEmpty() ? "no request" : FakeOpenAi.tools(AI.chat(0)).toString());
                return;
            }
            String result = toolResult();
            if (!result.contains("16:00") || !result.contains("Black Holes") || !result.contains("11")) {
                R.fail("show_times_tool", "the tool's result should be the schedule's shows for that date, with times and free seats.", "11:00 ..., 14:00 ..., 16:00 Black Holes, 11 seats", result);
                return;
            }
            R.pass("show_times_tool", "Three shows, with their free seats, straight from the schedule: the model can now tell a visitor that the 14:00 show is full.");
        });
    }
}
