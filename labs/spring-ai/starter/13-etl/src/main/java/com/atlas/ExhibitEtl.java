package com.atlas;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.springframework.ai.document.Document;
import org.springframework.ai.reader.markdown.MarkdownDocumentReader;
import org.springframework.ai.reader.markdown.config.MarkdownDocumentReaderConfig;
import org.springframework.ai.transformer.splitter.TokenTextSplitter;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.core.io.Resource;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;
import org.springframework.stereotype.Component;

/** At start-up: extract the exhibit cards, transform them into chunks, load the chunks into the vector store. */
@Component
public class ExhibitEtl implements ApplicationRunner {

    private final VectorStore store;
    private int files, documents, chunks;

    public ExhibitEtl(VectorStore store) {
        this.store = store;
    }

    @Override
    public void run(ApplicationArguments args) throws IOException {
        Resource[] cards = new PathMatchingResourcePatternResolver().getResources("classpath:exhibits/*.md");
        List<Document> read = read(cards);
        List<Document> stored = splitAndLoad(read);
        this.files = cards.length;
        this.documents = read.size();
        this.chunks = stored.size();
        System.out.println("ETL: " + files + " cards, " + documents + " documents, " + chunks + " chunks in the vector store.");
    }

    /** Extract: one or more Documents per card, each knowing which file it came from. */
    public List<Document> read(Resource[] cards) {
        // TODO (task read_cards): read every card with a MarkdownDocumentReader, adding the metadata file = the card's file name.
        return new ArrayList<>();
    }

    /** Transform and load: split into small chunks, then add them to the store. Returns the chunks. */
    public List<Document> splitAndLoad(List<Document> documents) {
        // TODO (task split_and_load): split into chunks of at most 100 tokens with a TokenTextSplitter, then add them to the store.
        return documents;
    }

    public Map<String, Integer> report() {
        return Map.of("files", files, "documents", documents, "chunks", chunks);
    }
}
