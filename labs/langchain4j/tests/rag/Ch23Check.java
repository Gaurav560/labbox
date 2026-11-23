package com.setu.check;

import java.nio.file.Path;
import java.util.List;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;

import com.setu.Rag;

import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.model.openai.OpenAiEmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingSearchRequest;
import dev.langchain4j.store.embedding.EmbeddingStore;

class Ch23Check {

    static final FakeOpenAi FAKE = new FakeOpenAi();

    @AfterAll
    static void stop() { FAKE.stop(); }

    static EmbeddingModel embed() {
        return OpenAiEmbeddingModel.builder().baseUrl(FAKE.baseUrl()).apiKey("k").modelName("ai-embed").build();
    }

    @Test
    void ingestRules() {
        R.task("ingest_rules", () -> {
            EmbeddingModel model = embed();
            EmbeddingStore<TextSegment> store = Rag.ingest(model, Path.of("docs"));
            var all = store.search(EmbeddingSearchRequest.builder().queryEmbedding(model.embed("instrument").content()).maxResults(50).minScore(0.0).build()).matches();
            if (all.isEmpty()) {
                R.fail("ingest_rules", "The store is empty. Load the documents with FileSystemDocumentLoader.loadDocuments(folder, new TextDocumentParser()) and ingest them with an EmbeddingStoreIngestor.");
                return;
            }
            if (all.size() < 6) {
                R.fail("ingest_rules", "The store has " + all.size() + " pieces: the documents were not split. Give the ingestor .documentSplitter(DocumentSplitters.recursive(300, 30)).",
                        "about 10 pieces of at most 300 characters", String.valueOf(all.size()));
                return;
            }
            String top = all.get(0).embedded().text();
            if (!top.contains("Musical instruments")) {
                R.fail("ingest_rules", "The closest piece to \"instrument\" should come from luggage.txt.", "Musical instruments up to 1.5 metres ...", top);
                return;
            }
            String file = all.get(0).embedded().metadata().getString("file_name");
            if (!"luggage.txt".equals(file)) {
                R.fail("ingest_rules", "Each piece should remember its file (metadata file_name): load the documents with FileSystemDocumentLoader.", "luggage.txt", String.valueOf(file));
                return;
            }
            R.pass("ingest_rules", "Five documents loaded, split into pieces, embedded and stored, each piece knowing its file: the indexing half of RAG.");
        });
    }

    @Test
    void ragAnswer() {
        R.task("rag_answer", () -> {
            EmbeddingModel model = embed();
            EmbeddingStore<TextSegment> store = new dev.langchain4j.store.embedding.inmemory.InMemoryEmbeddingStore<>();
            dev.langchain4j.store.embedding.EmbeddingStoreIngestor.builder()
                    .documentSplitter(dev.langchain4j.data.document.splitter.DocumentSplitters.recursive(300, 30))
                    .embeddingModel(model).embeddingStore(store).build()
                    .ingest(dev.langchain4j.data.document.loader.FileSystemDocumentLoader.loadDocuments(Path.of("docs"), new dev.langchain4j.data.document.parser.TextDocumentParser()));
            FAKE.reset();
            FAKE.script = b -> FakeOpenAi.Reply.text("Yes, instruments up to 1.5 metres travel free.");
            var chat = OpenAiChatModel.builder().baseUrl(FAKE.baseUrl()).apiKey("k").modelName("ai-chat").build();
            String got = Rag.assistant(chat, store, model).chat("Can I bring a musical instrument?");
            List<String> users = FakeOpenAi.texts(FAKE.chat(-1), "user");
            String user = users.isEmpty() ? "" : users.get(users.size() - 1);
            if (!user.contains("Musical instruments up to 1.5 metres")) {
                R.fail("rag_answer", "The model got the question without the rules. Build the Assistant with .contentRetriever(retriever(store, embeddingModel)), so the closest pieces travel with the question.",
                        "the question plus the luggage rules", user.length() > 160 ? user.substring(0, 160) + "..." : user);
                return;
            }
            if (!"Yes, instruments up to 1.5 metres travel free.".equals(got)) {
                R.fail("rag_answer", "chat(...) should return the model's answer.", "Yes, instruments up to 1.5 metres travel free.", String.valueOf(got));
                return;
            }
            R.pass("rag_answer", "Retrieval, then generation: the question went to the model with the railway's own rules attached.");
        });
    }
}
