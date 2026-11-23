package com.setu.check;

import java.util.List;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;

import com.setu.Http;

import tools.jackson.databind.JsonNode;

class Ch07Check {

    static final FakeOpenAi FAKE = new FakeOpenAi();

    @AfterAll
    static void stop() { FAKE.stop(); }

    @Test
    void sendRequest() {
        R.task("send_request", () -> {
            FAKE.reset();
            String got = Http.send(FAKE.baseUrl(), "lab-key-123", "Which trains do you run?");
            if (FAKE.chatRequests.isEmpty()) {
                R.fail("send_request", "Http.send did not reach the model: nothing was POSTed to " + FAKE.baseUrl() + "/chat/completions. Build an HttpRequest for that address, with POST(BodyPublishers.ofString(body(question))), and send it with CLIENT.");
                return;
            }
            String auth = FAKE.authorizations.get(FAKE.authorizations.size() - 1);
            if (!"Bearer lab-key-123".equals(auth)) {
                R.fail("send_request", "The request reached the model, but without the key: add the header Authorization with the value \"Bearer \" + apiKey.",
                        "Bearer lab-key-123", String.valueOf(auth));
                return;
            }
            String type = FAKE.contentTypes.get(FAKE.contentTypes.size() - 1);
            if (type == null || !type.startsWith("application/json")) {
                R.fail("send_request", "Add the header Content-Type: application/json, so the server knows the body is JSON.", "application/json", String.valueOf(type));
                return;
            }
            JsonNode req = FAKE.chat(-1);
            List<String> users = FakeOpenAi.texts(req, "user");
            if (!List.of("Which trains do you run?").equals(users)) {
                R.fail("send_request", "Send body(question) as the request body.", "[Which trains do you run?]", users.toString());
                return;
            }
            if (got == null || !got.contains("Hello from the fake model.")) {
                R.fail("send_request", "Http.send must return the response body (the JSON the server sent back) as a String: .body() of the HttpResponse.",
                        "the response JSON", String.valueOf(got));
                return;
            }
            R.pass("send_request", "One POST, two headers, a JSON body: that is all a call to a language model is.");
        });
    }

    @Test
    void readAnswer() {
        R.task("read_answer", () -> {
            String json = "{\"id\":\"x\",\"choices\":[{\"index\":0,\"message\":{\"role\":\"assistant\",\"content\":\"We run three trains: the \\\"Ghat Express\\\",\\nthe Konkan Breeze and the Monsoon Mail.\"},\"finish_reason\":\"stop\"}],\"usage\":{\"prompt_tokens\":10}}";
            String want = "We run three trains: the \"Ghat Express\",\nthe Konkan Breeze and the Monsoon Mail.";
            String got = Http.answer(json);
            if (!want.equals(got)) {
                R.fail("read_answer", "Http.answer did not return the answer's text. Read the JSON with JSON.readTree, then take path(\"choices\").path(0).path(\"message\").path(\"content\") as a String.",
                        want, String.valueOf(got));
                return;
            }
            R.pass("read_answer", "You read the answer straight out of the JSON, quotes and line breaks intact. Next chapter, a library does it for you.");
        });
    }
}
