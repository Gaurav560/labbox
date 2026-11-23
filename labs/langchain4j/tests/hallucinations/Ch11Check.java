package com.setu.check;

import java.util.List;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;

import com.setu.Honest;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import tools.jackson.databind.JsonNode;

class Ch11Check {

    static final FakeOpenAi FAKE = new FakeOpenAi();

    @AfterAll
    static void stop() { FAKE.stop(); }

    @Test
    void honestPrompt() {
        R.task("honest_prompt", () -> {
            String s = Honest.honestSystem();
            if (s == null || !s.contains("You are Setu")) {
                R.fail("honest_prompt", "Keep Setu's instructions: start from SYSTEM and add to it.", "SYSTEM plus a new instruction", String.valueOf(s));
                return;
            }
            if (!s.contains("I don't know")) {
                R.fail("honest_prompt", "Tell the model what to say when it does not know: your instruction must contain the words I don't know (with the apostrophe).",
                        "... say \"I don't know\" ...", s);
                return;
            }
            if (!s.toLowerCase().contains("invent") && !s.toLowerCase().contains("make up") && !s.toLowerCase().contains("guess")) {
                R.fail("honest_prompt", "Also forbid inventing: say it must never invent (or make up, or guess) times, fares or rules.");
                return;
            }
            R.pass("honest_prompt", "Permission to say I don't know is the cheapest defence against hallucinations.");
        });
    }

    @Test
    void groundedAnswer() {
        R.task("grounded_answer", () -> {
            FAKE.reset();
            FAKE.script = body -> FakeOpenAi.Reply.text("The Ghat Express leaves Pune at 07:15.");
            ChatModel model = OpenAiChatModel.builder().baseUrl(FAKE.baseUrl()).apiKey("k").modelName("ai-chat").build();
            String got = Honest.ask(model, "When does the Ghat Express leave Pune?");
            JsonNode req = FAKE.chat(-1);
            List<String> system = FakeOpenAi.texts(req, "system");
            String sys = system.isEmpty() ? "" : system.get(0);
            if (!sys.contains("Ghat Express: Pune 07:15")) {
                R.fail("grounded_answer", "The model never saw the timetable. Build the system message from honestSystem(), a blank line, \"Facts:\" and facts().",
                        "a system message containing the timetable", sys.length() > 120 ? sys.substring(0, 120) + "..." : sys);
                return;
            }
            if (!sys.contains("I don't know") || !sys.contains("Facts:")) {
                R.fail("grounded_answer", "Use honestSystem() (not SYSTEM) and put \"Facts:\" before the timetable, so the model knows what the facts are.");
                return;
            }
            if (!FakeOpenAi.texts(req, "user").equals(List.of("When does the Ghat Express leave Pune?"))) {
                R.fail("grounded_answer", "Send the question, unchanged, as the user message.");
                return;
            }
            if (!"The Ghat Express leaves Pune at 07:15.".equals(got)) {
                R.fail("grounded_answer", "Return the answer's text: aiMessage().text().", "The Ghat Express leaves Pune at 07:15.", String.valueOf(got));
                return;
            }
            R.pass("grounded_answer", "Facts in the prompt turn a confident guess into a checkable answer. Chapter 23 finds the right facts automatically.");
        });
    }
}
