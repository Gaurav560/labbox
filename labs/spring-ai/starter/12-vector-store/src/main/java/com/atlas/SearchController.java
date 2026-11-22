package com.atlas;

import java.util.List;

import org.springframework.ai.document.Document;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** Searches the exhibit cards by meaning. */
@RestController
public class SearchController {

    /** One search result: which card, how similar, and the start of its text. */
    public record Hit(String file, double score, String preview) {}

    private final VectorStore store;

    public SearchController(VectorStore store) {
        this.store = store;
    }

    /** GET /search?q=...&k=3 the k cards closest in meaning to q, best first, leaving out weak matches. */
    @GetMapping("/search")
    public List<Hit> search(@RequestParam String q, @RequestParam(defaultValue = "3") int k) {
        // TODO (task search_cards): ask the store for the k most similar cards, with a similarity threshold of 0.5.
        List<Document> found = List.of();
        return found.stream()
                .map(d -> new Hit((String) d.getMetadata().get("file"), d.getScore(), d.getText().substring(0, Math.min(80, d.getText().length()))))
                .toList();
    }
}
