package com.setu;

import com.openai.client.OpenAIClient;
import com.openai.client.okhttp.OpenAIOkHttpClient;
import com.openai.models.chat.completions.ChatCompletion;
import com.openai.models.chat.completions.ChatCompletionCreateParams;

/** The same call with OpenAI's official Java SDK: typed classes instead of hand-written JSON. */
public final class Sdk {

    static final String SYSTEM = "You are Setu, the help desk assistant of Sahyadri Rail, a small hill railway between Pune, Lonavala, Karjat and Ratnagiri. Answer passengers in at most three short sentences.";

    private Sdk() {
    }

    /** A client for an OpenAI-compatible server (here, the LabBox gateway). */
    public static OpenAIClient client(String baseUrl, String apiKey) {
        return OpenAIOkHttpClient.builder()
                .baseUrl(baseUrl)
                .apiKey(apiKey)
                .build();
    }

    /** One question, one answer, with typed request and response classes. */
    public static String ask(OpenAIClient client, String question) {
        ChatCompletionCreateParams params = ChatCompletionCreateParams.builder()
                .model("ai-chat")
                .addSystemMessage(SYSTEM)
                .addUserMessage(question)
                .build();
        ChatCompletion completion = client.chat().completions().create(params);
        return completion.choices().get(0).message().content().orElse("");
    }
}
