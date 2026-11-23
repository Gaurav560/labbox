package com.setu;

import java.nio.file.Path;
import java.util.List;

import dev.langchain4j.data.document.Document;
import dev.langchain4j.data.document.loader.FileSystemDocumentLoader;
import dev.langchain4j.data.document.parser.TextDocumentParser;
import dev.langchain4j.data.document.splitter.DocumentSplitters;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.rag.content.retriever.ContentRetriever;
import dev.langchain4j.rag.content.retriever.EmbeddingStoreContentRetriever;
import dev.langchain4j.service.AiServices;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.EmbeddingStoreIngestor;
import dev.langchain4j.store.embedding.inmemory.InMemoryEmbeddingStore;

/** Retrieval-augmented generation: Setu answers from the railway's own documents. */
public final class Rag {

    private Rag() {
    }

    /** Load, split, embed, store: the indexing half of RAG. */
    public static EmbeddingStore<TextSegment> ingest(EmbeddingModel model, Path folder) {
        List<Document> docs = FileSystemDocumentLoader.loadDocuments(folder, new TextDocumentParser());
        EmbeddingStore<TextSegment> store = new InMemoryEmbeddingStore<>();
        EmbeddingStoreIngestor.builder()
                .documentSplitter(DocumentSplitters.recursive(300, 30))
                .embeddingModel(model)
                .embeddingStore(store)
                .build()
                .ingest(docs);
        return store;
    }

    /** The retrieval half: every question is answered with the closest pieces of the documents. */
    public static Assistant assistant(ChatModel chatModel, EmbeddingStore<TextSegment> store, EmbeddingModel embeddingModel) {
        return AiServices.builder(Assistant.class)
                .chatModel(chatModel)
                .contentRetriever(retriever(store, embeddingModel))
                .build();
    }

    /** Finds the 3 pieces closest to a question, if they score at least 0.7. */
    public static ContentRetriever retriever(EmbeddingStore<TextSegment> store, EmbeddingModel embeddingModel) {
        return EmbeddingStoreContentRetriever.builder()
                .embeddingStore(store)
                .embeddingModel(embeddingModel)
                .maxResults(3)
                .minScore(0.7)
                .build();
    }
}
