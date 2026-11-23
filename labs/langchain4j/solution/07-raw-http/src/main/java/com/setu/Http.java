package com.setu;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;
import tools.jackson.databind.node.ObjectNode;

/** Talking to a language model with nothing but Java's own HTTP client and a JSON library. */
public final class Http {

    static final String SYSTEM = "You are Setu, the help desk assistant of Sahyadri Rail, a small hill railway between Pune, Lonavala, Karjat and Ratnagiri. Answer passengers in at most three short sentences.";
    static final JsonMapper JSON = JsonMapper.builder().build();
    // HTTP/1.1: by default Java offers to upgrade a plain http:// connection to HTTP/2, which some servers
    // (the LabBox gateway among them) answer with an error.
    static final HttpClient CLIENT = HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1).build();

    private Http() {
    }

    /** The request body: which model, and the messages (a system message, then the passenger's question). */
    public static String body(String question) {
        ObjectNode body = JSON.createObjectNode();
        body.put("model", "ai-chat");
        var messages = body.putArray("messages");
        messages.addObject().put("role", "system").put("content", SYSTEM);
        messages.addObject().put("role", "user").put("content", question);
        return body.toString();
    }

    /** One HTTP POST: the request body in, the response body (JSON) out. */
    public static String send(String baseUrl, String apiKey, String question) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder(URI.create(baseUrl + "/chat/completions"))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + apiKey)
                .POST(HttpRequest.BodyPublishers.ofString(body(question)))
                .build();
        return CLIENT.send(request, HttpResponse.BodyHandlers.ofString()).body();
    }

    /** The text of the first choice. */
    public static String answer(String responseJson) {
        JsonNode root = JSON.readTree(responseJson);
        return root.path("choices").path(0).path("message").path("content").asString();
    }
}
