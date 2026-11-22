package com.atlas;

import java.util.List;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** Atlas plans tours and suggests exhibits, as data the website can use, not just text. */
@RestController
public class TourController {

    /** One stop on a tour: which gallery, and for how many minutes. */
    public record Stop(String gallery, int minutes) {}

    /** A tour: a title and its stops, in order. */
    public record TourPlan(String title, List<Stop> stops) {}

    /** Suggested exhibits. A list inside a record: models answer with an object far more reliably than with a bare list. */
    public record Suggestions(List<String> exhibits) {}

    private final ChatClient chat;

    public TourController(ChatClient.Builder builder) {
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

    /** GET /tour?minutes=60 plans a tour that fits in that many minutes. */
    @GetMapping("/tour")
    public TourPlan tour(@RequestParam int minutes) {
        // TODO (task tour_plan): ask for a tour of the given length, and get the answer back as a TourPlan.
        return new TourPlan("Not planned yet", List.of());
    }

    /** GET /suggest?interest=space suggests three exhibit names. */
    @GetMapping("/suggest")
    public List<String> suggest(@RequestParam String interest) {
        // TODO (task exhibit_list): ask for three exhibits for this interest, as Suggestions, and return its list.
        return List.of();
    }
}
