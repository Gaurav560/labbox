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
        List<Document> all = new ArrayList<>();
        for (Resource card : cards) {
            MarkdownDocumentReaderConfig config = MarkdownDocumentReaderConfig.builder()
                    .withAdditionalMetadata("file", card.getFilename())
                    .build();
            all.addAll(new MarkdownDocumentReader(card, config).get());
        }
        return all;
    }

    /** Transform and load: split into small chunks, then add them to the store. Returns the chunks. */
    public List<Document> splitAndLoad(List<Document> documents) {
        List<Document> pieces = TokenTextSplitter.builder()
                .withChunkSize(100)
                .build()
                .apply(documents);
        store.add(pieces);
        return pieces;
    }

    public Map<String, Integer> report() {
        return Map.of("files", files, "documents", documents, "chunks", chunks);
    }
}
