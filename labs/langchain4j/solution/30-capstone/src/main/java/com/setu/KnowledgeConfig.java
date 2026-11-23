package com.setu;

import java.util.List;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import dev.langchain4j.data.document.Document;
import dev.langchain4j.data.document.loader.ClassPathDocumentLoader;
import dev.langchain4j.data.document.parser.TextDocumentParser;
import dev.langchain4j.data.document.splitter.DocumentSplitters;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.rag.content.retriever.ContentRetriever;
import dev.langchain4j.rag.content.retriever.EmbeddingStoreContentRetriever;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.EmbeddingStoreIngestor;
import dev.langchain4j.store.embedding.inmemory.InMemoryEmbeddingStore;

/** Setu's knowledge: the rule book in src/main/resources/rules, indexed once when the app starts. */
@Configuration
public class KnowledgeConfig {

    /** Load, split, embed, store: once, at start-up. */
    @Bean
    EmbeddingStore<TextSegment> rulesStore(EmbeddingModel embeddingModel) {
        List<Document> docs = ClassPathDocumentLoader.loadDocuments("rules", new TextDocumentParser());
        EmbeddingStore<TextSegment> store = new InMemoryEmbeddingStore<>();
        EmbeddingStoreIngestor.builder()
                .documentSplitter(DocumentSplitters.recursive(300, 30))
                .embeddingModel(embeddingModel)
                .embeddingStore(store)
                .build()
                .ingest(docs);
        return store;
    }

    /** The only ContentRetriever bean, so every @AiService uses it. */
    @Bean
    ContentRetriever rulesRetriever(EmbeddingStore<TextSegment> rulesStore, EmbeddingModel embeddingModel) {
        return EmbeddingStoreContentRetriever.builder()
                .embeddingStore(rulesStore)
                .embeddingModel(embeddingModel)
                .maxResults(3)
                .minScore(0.7)
                .build();
    }
}
