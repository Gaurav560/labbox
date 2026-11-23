package com.setu.check;

import java.lang.reflect.Method;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.List;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;

import com.setu.Assistant;
import com.setu.Desk;
import com.setu.RailTools;

import dev.langchain4j.agent.tool.Tool;
import dev.langchain4j.model.openai.OpenAiChatModel;
import tools.jackson.databind.JsonNode;

class Ch19Check {

    static final FakeOpenAi FAKE = new FakeOpenAi();

    @AfterAll
    static void stop() { FAKE.stop(); }

    @Test
    void dateTool() {
        R.task("date_tool", () -> {
            RailTools tools = new RailTools(Clock.fixed(Instant.parse("2026-11-23T08:00:00Z"), ZoneOffset.UTC));
            String got = tools.nextDate("saturday");
            if (!"2026-11-28".equals(got)) {
                R.fail("date_tool", "On Monday 2026-11-23, nextDate(\"saturday\") should be the coming Saturday. Turn the text into a DayOfWeek (trim, upper-case), then LocalDate.now(clock).with(TemporalAdjusters.next(day)).toString().",
                        "2026-11-28", String.valueOf(got));
                return;
            }
            if (!"2026-11-30".equals(tools.nextDate(" Monday "))) {
                R.fail("date_tool", "On a Monday, nextDate(\"Monday\") is the Monday after, a week later: TemporalAdjusters.next, not nextOrSame.", "2026-11-30", tools.nextDate(" Monday "));
                return;
            }
            Method m = RailTools.class.getMethod("nextDate", String.class);
            if (m.getAnnotation(Tool.class) == null) {
                R.fail("date_tool", "The method works, but the model cannot see it: annotate nextDate with @Tool(\"The date (YYYY-MM-DD) of the next given day of the week, after today\").");
                return;
            }
            if (m.getParameters()[0].getAnnotation(dev.langchain4j.agent.tool.P.class) == null) {
                R.fail("date_tool", "Describe the parameter for the model: @P(\"day of the week in English, for example SATURDAY\").");
                return;
            }
            R.pass("date_tool", "Java does the calendar arithmetic; the model only has to ask. No more Thursdays for Saturday.");
        });
    }

    @Test
    void toolsInService() {
        R.task("tools_in_service", () -> {
            FAKE.reset();
            // First request: the model asks for the tool. Second request (with the tool's result): it answers.
            FAKE.script = body -> FAKE.chatRequests.size() == 1
                    ? FakeOpenAi.Reply.tool("fare", "{\"destination\": \"Karjat\"}")
                    : FakeOpenAi.Reply.text("Three tickets to Karjat cost Rs 420.");
            Assistant setu = Desk.assistant(OpenAiChatModel.builder().baseUrl(FAKE.baseUrl()).apiKey("k").modelName("ai-chat").build(), new RailTools());
            String got;
            try {
                got = setu.chat("How much are 3 tickets to Karjat?");
            } catch (RuntimeException e) {
                R.fail("tools_in_service", "The model asked for the fare tool, but Setu has no tools, so LangChain4j stopped (\"no such tool exists\"). Build the Assistant with AiServices.builder(Assistant.class), .chatModel(model) and .tools(tools).");
                return;
            }
            JsonNode first = FAKE.chat(0);
            List<String> tools = FakeOpenAi.tools(first);
            if (!tools.contains("fare") || !tools.contains("nextDate")) {
                R.fail("tools_in_service", "The model was not offered RailTools' methods. Build the Assistant with AiServices.builder(Assistant.class), .chatModel(model) and .tools(tools).",
                        "[fare, nextDate]", tools.toString());
                return;
            }
            if (FAKE.chatRequests.size() < 2 || !FAKE.chatRequests.get(1).contains("140")) {
                R.fail("tools_in_service", "The model asked for fare(Karjat), but the result never came back to it. Let AiServices run the tools: pass them with .tools(tools).");
                return;
            }
            if (!"Three tickets to Karjat cost Rs 420.".equals(got)) {
                R.fail("tools_in_service", "chat(...) should return the model's final answer, after the tool ran.", "Three tickets to Karjat cost Rs 420.", String.valueOf(got));
                return;
            }
            R.pass("tools_in_service", "The model asked, LangChain4j ran fare(\"Karjat\") in Java, and the real price went back to the model.");
        });
    }
}
