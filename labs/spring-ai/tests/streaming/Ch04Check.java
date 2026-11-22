package com.atlas.check;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;

/** Chapter 4: streaming, read over a real HTTP connection. */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class Ch04Check {
    static final FakeOpenAi AI = new FakeOpenAi();
    static final String ANSWER = "The planetarium show starts at four o'clock.";

    @DynamicPropertySource
    static void ai(DynamicPropertyRegistry r) {
        r.add("spring.ai.openai.base-url", AI::baseUrl);
        r.add("spring.ai.openai.api-key", () -> "check-key");
    }

    @AfterAll
    static void stop() {
        AI.stop();
    }

    @LocalServerPort
    int port;

    String stream(String path) throws Exception {
        HttpRequest req = HttpRequest.newBuilder(URI.create("http://127.0.0.1:" + port + path))
                .header("Accept", "text/event-stream").timeout(Duration.ofSeconds(20)).build();
        return HttpClient.newHttpClient().send(req, HttpResponse.BodyHandlers.ofString()).body();
    }

    /** Joins the data lines of an event stream back into text. */
    static String data(String body) {
        StringBuilder b = new StringBuilder();
        for (String line : body.split("\n")) {
            if (line.startsWith("data:")) b.append(line.substring(5));
        }
        return b.toString();
    }

    @Test
    void streamAnswer() {
        R.task("stream_answer", () -> {
            AI.reset();
            AI.script = b -> FakeOpenAi.Reply.text(ANSWER);
            String body = stream("/stream?q=When%20is%20the%20show%3F");
            if (AI.chatRequests.isEmpty()) {
                R.fail("stream_answer", "GET /stream never called the model.", "the answer, piece by piece", body);
                return;
            }
            if (!AI.chat(-1).path("stream").asBoolean(false)) {
                R.fail("stream_answer", "the model was asked for the whole answer at once. Use .stream().content() instead of .call().content().");
                return;
            }
            String text = data(body);
            if (!text.replace(" ", "").equals(ANSWER.replace(" ", "")) || body.split("data:").length < 4) {
                R.fail("stream_answer", "/stream should send the model's pieces as they arrive, as server-sent events.", ANSWER, text);
                return;
            }
            R.pass("stream_answer", "The answer arrived in " + (body.split("data:").length - 1) + " pieces, each sent the moment the model wrote it.");
        });
    }

    @Test
    void streamEvents() {
        R.task("stream_events", () -> {
            AI.reset();
            AI.script = b -> FakeOpenAi.Reply.text(ANSWER);
            String body = stream("/stream/events?q=When%20is%20the%20show%3F");
            if (AI.chatRequests.isEmpty() || !AI.chat(-1).path("stream").asBoolean(false)) {
                R.fail("stream_events", "GET /stream/events should stream the model's answer, like /stream.", "events named token, then done", body.length() > 200 ? body.substring(0, 200) : body);
                return;
            }
            long tokens = body.lines().filter(l -> l.equals("event:token")).count();
            if (tokens < 3) {
                R.fail("stream_events", "each piece of the answer should be an event named token: ServerSentEvent.builder(piece).event(\"token\").build().", "event:token for each piece", body.length() > 200 ? body.substring(0, 200) : body);
                return;
            }
            String[] lines = body.strip().split("\n");
            boolean doneLast = false;
            for (int i = lines.length - 1; i >= 0; i--) {
                if (lines[i].startsWith("event:")) {
                    doneLast = lines[i].equals("event:done");
                    break;
                }
            }
            if (!doneLast) {
                R.fail("stream_events", "after the last piece, send one more event named done, so the page knows the answer is complete. Flux has concatWith(...).");
                return;
            }
            R.pass("stream_events", tokens + " token events, then done: a page can show the answer as it grows and know when it is finished.");
        });
    }
}
