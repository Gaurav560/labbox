package com.setu.check;

import java.util.List;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;

import com.setu.Desk;
import com.setu.Models;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import tools.jackson.databind.JsonNode;

class Ch09Check {

    static final FakeOpenAi FAKE = new FakeOpenAi();

    @AfterAll
    static void stop() { FAKE.stop(); }

    @Test
    void chatModel() {
        R.task("chat_model", () -> {
            FAKE.reset();
            ChatModel model = Models.chatModel(FAKE.baseUrl(), "lab-key-9");
            if (model == null) {
                R.fail("chat_model", "Models.chatModel returned null. Build one with OpenAiChatModel.builder(): .baseUrl(baseUrl), .apiKey(apiKey), .modelName(\"ai-chat\"), then .build().");
                return;
            }
            String got = model.chat("Hello");
            JsonNode req = FAKE.chat(-1);
            if (!"ai-chat".equals(req.path("model").asString())) {
                R.fail("chat_model", "The model name must be \"ai-chat\", the alias of this course's model: .modelName(\"ai-chat\").", "ai-chat", req.path("model").asString());
                return;
            }
            String auth = FAKE.authorizations.get(FAKE.authorizations.size() - 1);
            if (!"Bearer lab-key-9".equals(auth)) {
                R.fail("chat_model", "Pass the apiKey to the builder with .apiKey(apiKey).", "Bearer lab-key-9", String.valueOf(auth));
                return;
            }
            if (!"Hello from the fake model.".equals(got)) {
                R.fail("chat_model", "model.chat(\"Hello\") did not return the model's text.", "Hello from the fake model.", String.valueOf(got));
                return;
            }
            R.pass("chat_model", "Your first LangChain4j model. Notice the type you return: ChatModel, an interface any provider can implement.");
        });
    }

    @Test
    void systemMessage() {
        R.task("system_message", () -> {
            FAKE.reset();
            FAKE.script = body -> FakeOpenAi.Reply.text("Hello! I am Setu, the help desk assistant of Sahyadri Rail.");
            ChatModel model = OpenAiChatModel.builder().baseUrl(FAKE.baseUrl()).apiKey("k").modelName("ai-chat").build();
            String got = Desk.ask(model, "Who are you?");
            JsonNode req = FAKE.chat(-1);
            List<String> system = FakeOpenAi.texts(req, "system");
            List<String> user = FakeOpenAi.texts(req, "user");
            if (system.isEmpty()) {
                R.fail("system_message", "The model got no system message, so it does not know it is Setu. Pass SystemMessage.from(SYSTEM) to model.chat(...), before the UserMessage.");
                return;
            }
            if (!system.get(0).contains("You are Setu")) {
                R.fail("system_message", "The system message should be SYSTEM, Setu's instructions.", "You are Setu, ...", system.get(0));
                return;
            }
            if (!List.of("Who are you?").equals(user)) {
                R.fail("system_message", "Send the question as UserMessage.from(question), after the system message.", "[Who are you?]", user.toString());
                return;
            }
            if (!"Hello! I am Setu, the help desk assistant of Sahyadri Rail.".equals(got)) {
                R.fail("system_message", "Return the answer's text: model.chat(...) gives a ChatResponse; its aiMessage().text() is the answer.",
                        "Hello! I am Setu, ...", String.valueOf(got));
                return;
            }
            R.pass("system_message", "Instructions in a system message, the question in a user message: the shape of almost every AI feature.");
        });
    }
}
