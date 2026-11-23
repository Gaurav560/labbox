package com.atlas;

import org.springframework.ai.embedding.EmbeddingModel;
import org.springframework.ai.vectorstore.SimpleVectorStore;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/** Where the exhibit cards' embeddings are kept. In memory here; a real museum would use PGvector or another database. */
@Configuration
public class VectorStoreConfig {

    @Bean
    VectorStore vectorStore(EmbeddingModel embeddings) {
        return SimpleVectorStore.builder(embeddings).build();
    }
}
