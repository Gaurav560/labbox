package com.atlas;

import java.io.IOException;
import java.util.List;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.util.MimeType;
import org.springframework.util.MimeTypeUtils;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

/** Visitors photograph an exhibit and ask Atlas about it. */
@RestController
public class LookController {

    /** Which exhibit a photo shows, and the clue in the photo that gave it away. */
    public record Sighting(String exhibit, String clue) {}

    /** The museum's exhibits, by the names on their labels. */
    static final List<String> EXHIBITS = List.of("Foucault pendulum", "Planetarium dome", "Mangalyaan model",
            "Vikram lander model", "Rajasaurus skull", "DNA double helix", "Camera obscura", "Prism room",
            "Whispering dishes", "Bicycle generator", "Solar tree");

    private final ChatClient chat;

    public LookController(ChatClient.Builder builder) {
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

    /** POST /look with a photo (form field image) and a question (q). */
    @PostMapping("/look")
    public String look(@RequestParam MultipartFile image,
                       @RequestParam(defaultValue = "What is in this photo?") String q) throws IOException {
        MimeType type = MimeTypeUtils.IMAGE_JPEG;
        ByteArrayResource picture = new ByteArrayResource(Photos.shrink(image.getBytes(), 512));
        return chat.prompt()
                .user(u -> u.text(q).media(type, picture))
                .call()
                .content();
    }

    /** POST /identify with a photo: which of the museum's exhibits it shows. */
    @PostMapping("/identify")
    public Sighting identify(@RequestParam MultipartFile image) throws IOException {
        MimeType type = MimeTypeUtils.IMAGE_JPEG;
        ByteArrayResource picture = new ByteArrayResource(Photos.shrink(image.getBytes(), 512));
        String names = String.join(", ", EXHIBITS);
        return chat.prompt()
                .user(u -> u.text("Which of these exhibits does the photo show: " + names
                        + "? If it shows none of them, answer none.").media(type, picture))
                .call()
                .entity(Sighting.class);
    }
}
