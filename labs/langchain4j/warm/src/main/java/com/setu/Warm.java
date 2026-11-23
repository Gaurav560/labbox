package com.setu;

import dev.langchain4j.data.document.Document;
import dev.langchain4j.model.embedding.onnx.bgesmallenv15q.BgeSmallEnV15QuantizedEmbeddingModel;
import dev.langchain4j.model.ollama.OllamaChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.model.openai.OpenAiTokenCountEstimator;
import dev.langchain4j.store.embedding.inmemory.InMemoryEmbeddingStore;

/** Runs once at image build: loads each library so its classes (and the local embedding model) are cached. */
public class Warm {

    public static void main(String[] args) {
        OpenAiChatModel.builder().baseUrl("http://127.0.0.1:1").apiKey("x").modelName("ai-chat").build();
        OllamaChatModel.builder().baseUrl("http://127.0.0.1:1").modelName("llama3.2").build();
        System.out.println("tokens: " + new OpenAiTokenCountEstimator("gpt-4o-mini").estimateTokenCountInText("Sahyadri Rail"));
        var model = new BgeSmallEnV15QuantizedEmbeddingModel();
        System.out.println("dimensions: " + model.embed("Pune to Lonavala").content().dimension());
        new InMemoryEmbeddingStore<>();
        Document.from("warm");
        com.openai.client.okhttp.OpenAIOkHttpClient.builder().apiKey("x").baseUrl("http://127.0.0.1:1").build();
    }
}
