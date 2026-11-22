package com.atlas;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.http.MediaType;
import org.springframework.http.codec.ServerSentEvent;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Flux;

/** Atlas answers as it thinks: word by word, as a stream. */
@RestController
public class StreamController {

    private final ChatClient chat;

    public StreamController(ChatClient.Builder builder) {
        this.chat = builder
                .defaultSystem("""
            You are Atlas, the friendly visitor guide of the Deccan Science Museum in Pune.
            Answer in at most three short sentences, in plain, simple words.
            You may answer questions about the museum, its exhibits, and any science topic.
            For anything else, say kindly that you are the museum's guide.
            Never invent opening hours, prices or exhibits: if you do not know, say so.
            """)
                .build();
    }

    /** GET /stream?q=... sends the answer piece by piece, as server-sent events. */
    @GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> stream(@RequestParam String q) {
        // TODO (task stream_answer): stream the model's answer instead of waiting for all of it.
        return Flux.just("Not streaming yet.");
    }

    /** GET /stream/events?q=... the same, as named events: "token" for each piece, then one "done". */
    @GetMapping(value = "/stream/events", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<ServerSentEvent<String>> events(@RequestParam String q) {
        // TODO (task stream_events): each piece as an event named "token", then one event named "done".
        return Flux.just(ServerSentEvent.builder("Not streaming yet.").build());
    }
}
