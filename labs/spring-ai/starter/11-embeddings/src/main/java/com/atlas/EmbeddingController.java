package com.atlas;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.springframework.ai.embedding.EmbeddingModel;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** Turns text into numbers, and finds the exhibit whose description means the most like a question. */
@RestController
public class EmbeddingController {

    /** Six exhibits, in one line each. */
    static final Map<String, String> EXHIBITS = new LinkedHashMap<>();

    static {
        EXHIBITS.put("Foucault pendulum", "A heavy ball on a long wire whose swing slowly turns as the Earth rotates.");
        EXHIBITS.put("Planetarium dome", "A domed theatre where shows project the night sky, the planets and the stars.");
        EXHIBITS.put("Rajasaurus", "The skull of a horned meat-eating dinosaur found in Gujarat.");
        EXHIBITS.put("Prism room", "Sunlight through a glass prism spreads into a rainbow of colours.");
        EXHIBITS.put("Whispering dishes", "Two curved dishes carry a whisper fifteen metres across the gallery.");
        EXHIBITS.put("Bicycle generator", "Pedal a bicycle to make electricity and light up bulbs.");
    }

    private final EmbeddingModel embeddings;

    public EmbeddingController(EmbeddingModel embeddings) {
        this.embeddings = embeddings;
    }

    /** GET /embed?text=... the size of the text's embedding, and its first five numbers. */
    @GetMapping("/embed")
    public Map<String, Object> embed(@RequestParam String text) {
        float[] vector = embeddings.embed(text);
        float[] first = new float[Math.min(5, vector.length)];
        System.arraycopy(vector, 0, first, 0, first.length);
        return Map.of("dimensions", vector.length, "first", first);
    }

    /** GET /nearest?q=... the exhibit whose description is closest in meaning to the question. */
    @GetMapping("/nearest")
    public String nearest(@RequestParam String q) {
        // TODO (task nearest_exhibit): embed the question and every description; return the name with the highest cosine similarity.
        return "Not written yet.";
    }
}
