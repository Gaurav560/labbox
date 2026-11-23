package com.setu.check;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;

import com.setu.Assistant;
import com.setu.Desk;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.service.AiServices;
import tools.jackson.databind.JsonNode;

class Ch13Check {

    static final FakeOpenAi FAKE = new FakeOpenAi();

    @AfterAll
    static void stop() { FAKE.stop(); }

    static ChatModel model() {
        return OpenAiChatModel.builder().baseUrl(FAKE.baseUrl()).apiKey("k").modelName("ai-chat").build();
    }

    @Test
    void aiService() {
        R.task("ai_service", () -> {
            FAKE.reset();
            FAKE.script = b -> FakeOpenAi.Reply.text("Hello! I am Setu.");
            Assistant setu = Desk.assistant(model());
            if (setu == null) {
                R.fail("ai_service", "Desk.assistant returned null. Return AiServices.create(Assistant.class, model): LangChain4j writes the class for you.");
                return;
            }
            String got = setu.chat("Who are you?");
            if (FAKE.chatRequests.isEmpty() || !FakeOpenAi.texts(FAKE.chat(-1), "user").equals(List.of("Who are you?"))) {
                R.fail("ai_service", "Calling chat(...) on your assistant should send the question to the model as the user message.");
                return;
            }
            if (!"Hello! I am Setu.".equals(got)) {
                R.fail("ai_service", "chat(...) should return the model's answer.", "Hello! I am Setu.", String.valueOf(got));
                return;
            }
            R.pass("ai_service", "An interface and one line: LangChain4j made the implementation, request, response and all.");
        });
    }

    @Test
    void systemAnnotation() {
        R.task("system_annotation", () -> {
            FAKE.reset();
            AiServices.create(Assistant.class, model()).chat("Hello");
            JsonNode req = FAKE.chat(-1);
            List<String> system = FakeOpenAi.texts(req, "system");
            String want = Files.readString(Path.of("src/main/resources/setu-system.txt")).strip();
            if (system.isEmpty()) {
                R.fail("system_annotation", "The model got no system message. Annotate chat(...) in Assistant.java with @SystemMessage(fromResource = \"setu-system.txt\") (import dev.langchain4j.service.SystemMessage).");
                return;
            }
            if (!want.equals(system.get(0).strip())) {
                R.fail("system_annotation", "The system message should be the text of setu-system.txt: use fromResource = \"setu-system.txt\".", want, system.get(0));
                return;
            }
            R.pass("system_annotation", "Instructions in a resource file, attached by an annotation: no prompt text mixed into your Java code.");
        });
    }
}
