package com.setu.check;

import java.util.List;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;

import com.openai.client.OpenAIClient;
import com.openai.client.okhttp.OpenAIOkHttpClient;
import com.openai.models.chat.completions.ChatCompletionCreateParams;
import com.setu.Sdk;

import tools.jackson.databind.JsonNode;

class Ch08Check {

    static final FakeOpenAi FAKE = new FakeOpenAi();

    @AfterAll
    static void stop() { FAKE.stop(); }

    @Test
    void sdkClient() {
        R.task("sdk_client", () -> {
            FAKE.reset();
            OpenAIClient client = Sdk.client(FAKE.baseUrl(), "lab-key-8");
            if (client == null) {
                R.fail("sdk_client", "Sdk.client returned null. Build one with OpenAIOkHttpClient.builder(), then .baseUrl(baseUrl), .apiKey(apiKey) and .build().");
                return;
            }
            client.chat().completions().create(ChatCompletionCreateParams.builder().model("ai-chat").addUserMessage("ping").build());
            String auth = FAKE.authorizations.isEmpty() ? null : FAKE.authorizations.get(FAKE.authorizations.size() - 1);
            if (!"Bearer lab-key-8".equals(auth)) {
                R.fail("sdk_client", "The client reached the server without the right key: pass apiKey to the builder.", "Bearer lab-key-8", String.valueOf(auth));
                return;
            }
            R.pass("sdk_client", "A typed client for any OpenAI-compatible server: here the gateway, in production OpenAI itself.");
        });
    }

    @Test
    void sdkAsk() {
        R.task("sdk_ask", () -> {
            FAKE.reset();
            FAKE.script = body -> FakeOpenAi.Reply.text("We run the Ghat Express, the Konkan Breeze and the Monsoon Mail.");
            OpenAIClient client = OpenAIOkHttpClient.builder().baseUrl(FAKE.baseUrl()).apiKey("k").build();
            String got = Sdk.ask(client, "Which trains do you run?");
            if (FAKE.chatRequests.isEmpty()) {
                R.fail("sdk_ask", "Sdk.ask did not call the model. Build ChatCompletionCreateParams and pass them to client.chat().completions().create(...).");
                return;
            }
            JsonNode req = FAKE.chat(-1);
            if (!"ai-chat".equals(req.path("model").asString())) {
                R.fail("sdk_ask", "Use the model \"ai-chat\": .model(\"ai-chat\") on the params builder.", "ai-chat", req.path("model").asString());
                return;
            }
            List<String> system = FakeOpenAi.texts(req, "system");
            List<String> user = FakeOpenAi.texts(req, "user");
            if (system.isEmpty() || !system.get(0).contains("You are Setu")) {
                R.fail("sdk_ask", "Send Setu's instructions first, with .addSystemMessage(SYSTEM).", "a system message with SYSTEM", system.toString());
                return;
            }
            if (!List.of("Which trains do you run?").equals(user)) {
                R.fail("sdk_ask", "Send the question as the user message, with .addUserMessage(question).", "[Which trains do you run?]", user.toString());
                return;
            }
            if (!"We run the Ghat Express, the Konkan Breeze and the Monsoon Mail.".equals(got)) {
                R.fail("sdk_ask", "Return the answer's text: completion.choices().get(0).message().content(), which is an Optional, so .orElse(\"\").",
                        "We run the Ghat Express, the Konkan Breeze and the Monsoon Mail.", String.valueOf(got));
                return;
            }
            R.pass("sdk_ask", "The same call as chapter 7, with typed builders and no JSON by hand.");
        });
    }
}
