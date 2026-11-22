package com.atlas;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.springframework.ai.document.Document;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.core.io.Resource;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;
import org.springframework.stereotype.Component;

/** At start-up, puts every exhibit card into the vector store: one Document per card. */
@Component
public class CardLoader implements ApplicationRunner {

    private final VectorStore store;

    public CardLoader(VectorStore store) {
        this.store = store;
    }

    @Override
    public void run(ApplicationArguments args) throws IOException {
        List<Document> documents = new ArrayList<>();
        for (Resource card : new PathMatchingResourcePatternResolver().getResources("classpath:exhibits/*.md")) {
            String text = card.getContentAsString(StandardCharsets.UTF_8);
            documents.add(new Document(text, Map.of("file", card.getFilename())));
        }
        // TODO (task add_documents): add the documents to the vector store (it embeds them as it stores them).
    }
}
