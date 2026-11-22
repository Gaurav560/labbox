package com.atlas;

import java.util.List;
import java.util.Map;

import org.springframework.ai.document.Document;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** What the ETL did, and a search to see the chunks. */
@RestController
public class EtlController {

    public record Hit(String file, double score, String text) {}

    private final ExhibitEtl etl;
    private final VectorStore store;

    public EtlController(ExhibitEtl etl, VectorStore store) {
        this.etl = etl;
        this.store = store;
    }

    /** GET /etl: how many files, documents and chunks. */
    @GetMapping("/etl")
    public Map<String, Integer> report() {
        return etl.report();
    }

    /** GET /search?q=...: the three closest chunks. */
    @GetMapping("/search")
    public List<Hit> search(@RequestParam String q) {
        return store.similaritySearch(SearchRequest.builder().query(q).topK(3).build()).stream()
                .map(d -> new Hit((String) d.getMetadata().get("file"), d.getScore(), d.getText()))
                .toList();
    }
}
