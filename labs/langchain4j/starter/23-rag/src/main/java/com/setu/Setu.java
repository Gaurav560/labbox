package com.setu;

import java.nio.file.Path;

import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.model.openai.OpenAiEmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingStore;

/** Chapter 23: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) {
        String url = System.getenv("OPENAI_BASE_URL");
        String key = System.getenv("OPENAI_API_KEY");
        ChatModel chat = OpenAiChatModel.builder().baseUrl(url).apiKey(key).modelName("ai-chat").temperature(0.0).build();
        EmbeddingModel embed = OpenAiEmbeddingModel.builder().baseUrl(url).apiKey(key).modelName("ai-embed").build();

        EmbeddingStore<TextSegment> store = Rag.ingest(embed, Path.of("docs"));
        Assistant setu = Rag.assistant(chat, store, embed);
        for (String q : new String[] {"My train was cancelled because of a landslide. Do I get my money back?",
                "Can I bring my guitar?", "Is there wifi on the Monsoon Mail?"}) {
            System.out.println("> " + q);
            System.out.println(setu.chat(q) + "\n");
        }
    }
}
