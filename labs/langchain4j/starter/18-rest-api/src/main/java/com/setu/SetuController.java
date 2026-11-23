package com.setu;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

/** Setu's web API: the railway's website and app call it. */
@RestController
public class SetuController {

    /** What the website sends: who is asking, and the message. */
    public record ChatRequest(String passenger, String message) {
    }

    /** What Setu sends back. */
    public record ChatReply(String passenger, String answer) {
    }

    private final SetuAssistant setu;

    public SetuController(SetuAssistant setu) {
        this.setu = setu;
    }

    // TODO (task chat_endpoint): POST /chat. Take a ChatRequest from the request body, ask
    //   setu.chat(passenger, message), and return a ChatReply with the passenger and the answer.
}
