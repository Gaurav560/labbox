package com.setu.check;

import java.util.List;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;

import com.setu.Announcements;
import com.setu.StationDesk;

import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.service.AiServices;
import tools.jackson.databind.JsonNode;

class Ch14Check {

    static final FakeOpenAi FAKE = new FakeOpenAi();

    @AfterAll
    static void stop() { FAKE.stop(); }

    @Test
    void promptTemplate() {
        R.task("prompt_template", () -> {
            String want = "Write one short, calm station announcement in English and Marathi: the Monsoon Mail to Karjat "
                    + "is running 10 minutes late. Apologise once.";
            String got = Announcements.delayPrompt("Monsoon Mail", "Karjat", 10);
            if (!want.equals(got)) {
                String hint = got != null && got.contains("{{")
                        ? "Some blanks are still empty: the keys of the map must be exactly train, destination and minutes."
                        : "Fill the template with DELAY.apply(Map.of(\"train\", train, \"destination\", destination, \"minutes\", minutes)) and return .text().";
                R.fail("prompt_template", "delayPrompt(\"Monsoon Mail\", \"Karjat\", 10) is not the filled-in template. " + hint, want, String.valueOf(got));
                return;
            }
            R.pass("prompt_template", "One template, any train: the wording stays tested and the same, only the blanks change.");
        });
    }

    @Test
    void templateService() {
        R.task("template_service", () -> {
            FAKE.reset();
            StationDesk desk;
            try {
                desk = AiServices.create(StationDesk.class, OpenAiChatModel.builder().baseUrl(FAKE.baseUrl()).apiKey("k").modelName("ai-chat").build());
                desk.ask("Lonavala", "Where is the cloakroom?");
            } catch (RuntimeException e) {
                R.fail("template_service", "LangChain4j could not use StationDesk.ask: " + String.valueOf(e.getMessage()).lines().findFirst().orElse("")
                        + ". Add @UserMessage(\"A passenger at {{station}} station asks: {{question}}\") to the method, and @V(\"station\"), @V(\"question\") to its parameters.");
                return;
            }
            JsonNode req = FAKE.chat(-1);
            List<String> user = FakeOpenAi.texts(req, "user");
            String want = "A passenger at Lonavala station asks: Where is the cloakroom?";
            if (!List.of(want).equals(user)) {
                R.fail("template_service", "The user message should be the filled-in template. Check the @UserMessage text and the names in @V(...).", want, user.toString());
                return;
            }
            R.pass("template_service", "The template lives in the annotation, the values come from the method's parameters: a prompt with a type signature.");
        });
    }
}
