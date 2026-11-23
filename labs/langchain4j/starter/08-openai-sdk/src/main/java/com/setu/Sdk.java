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

    // TODO (task sdk_client): build an OpenAIClient with OpenAIOkHttpClient.builder(), giving it baseUrl and apiKey.
    public static OpenAIClient client(String baseUrl, String apiKey) {
        return null;
    }

    // TODO (task sdk_ask): build ChatCompletionCreateParams with model "ai-chat", the SYSTEM message and the question
    //   as the user message; send it with client.chat().completions().create(...);
    //   return the first choice's message content (it is an Optional: use orElse("")).
    public static String ask(OpenAIClient client, String question) {
        return "";
    }
}
