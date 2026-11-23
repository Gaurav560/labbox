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

    // TODO (task ingest_rules): load every document in the folder and put it in a new InMemoryEmbeddingStore:
    //   List<Document> docs = FileSystemDocumentLoader.loadDocuments(folder, new TextDocumentParser());
    //   then EmbeddingStoreIngestor.builder() with documentSplitter(DocumentSplitters.recursive(300, 30)),
    //   embeddingModel(model) and embeddingStore(store); build(), and ingest(docs). Return the store.
    public static EmbeddingStore<TextSegment> ingest(EmbeddingModel model, Path folder) {
        return new InMemoryEmbeddingStore<>();
    }

    // TODO (task rag_answer): build the Assistant with AiServices.builder(Assistant.class), the chat model, and
    //   .contentRetriever(retriever(store, embeddingModel)), so every question brings the closest pieces with it.
    public static Assistant assistant(ChatModel chatModel, EmbeddingStore<TextSegment> store, EmbeddingModel embeddingModel) {
        return AiServices.create(Assistant.class, chatModel);
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
