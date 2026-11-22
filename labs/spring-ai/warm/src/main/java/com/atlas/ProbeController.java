// Not a lesson: exercises every library once while the image is built.
package com.atlas;

import java.util.List;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.MessageChatMemoryAdvisor;
import org.springframework.ai.chat.client.advisor.vectorstore.QuestionAnswerAdvisor;
import org.springframework.ai.chat.memory.ChatMemory;
import org.springframework.ai.chat.memory.MessageWindowChatMemory;
import org.springframework.ai.chat.model.ChatResponse;
import org.springframework.ai.document.Document;
import org.springframework.ai.embedding.EmbeddingModel;
import org.springframework.ai.openai.OpenAiChatOptions;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.SimpleVectorStore;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Flux;

@RestController
public class ProbeController {
    record Stop(String gallery, int minutes) {}
    record TourPlan(String title, List<Stop> stops) {}

    static class MuseumTools {
        @Tool(description = "Opening hours of the museum on a day of the week")
        String openingHours(@ToolParam(description = "day of the week, like MONDAY") String day) {
            return day.equals("MONDAY") ? "closed" : "10:00 to 18:00";
        }
    }

    private final ChatClient chat;
    private final EmbeddingModel embeddings;
    private final SimpleVectorStore store;
    private final ChatMemory memory = MessageWindowChatMemory.builder().maxMessages(10).build();

    ProbeController(ChatClient.Builder builder, EmbeddingModel embeddings) {
        this.chat = builder.defaultSystem("You are Atlas, the guide of the Deccan Science Museum.").build();
        this.embeddings = embeddings;
        this.store = SimpleVectorStore.builder(embeddings).build();
    }

    @GetMapping("/ask")
    String ask(@RequestParam String q) {
        return chat.prompt().user(q).options(OpenAiChatOptions.builder().temperature(0.2).maxTokens(200)).call().content();
    }

    @GetMapping("/usage")
    String usage(@RequestParam String q) {
        ChatResponse r = chat.prompt().user(q).call().chatResponse();
        return r.getResult().getOutput().getText() + " | tokens=" + r.getMetadata().getUsage().getTotalTokens();
    }

    @GetMapping("/plan")
    TourPlan plan() {
        return chat.prompt().user("Plan a short tour").call().entity(TourPlan.class);
    }

    @GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    Flux<String> stream(@RequestParam String q) {
        return chat.prompt().user(q).stream().content();
    }

    @GetMapping("/hours")
    String hours(@RequestParam String q) {
        return chat.prompt().user(q).tools(new MuseumTools()).call().content();
    }

    @GetMapping("/embed")
    int embed(@RequestParam String q) {
        return embeddings.embed(q).length;
    }

    @GetMapping("/rag")
    String rag(@RequestParam String q) {
        if (store.similaritySearch(SearchRequest.builder().query("x").topK(1).build()).isEmpty()) {
            store.add(List.of(new Document("The Foucault pendulum is in Gallery 2."), new Document("The planetarium show starts at 4 pm.")));
        }
        return chat.prompt().user(q).advisors(QuestionAnswerAdvisor.builder(store).build()).call().content();
    }

    @GetMapping("/chat")
    String chatWithMemory(@RequestParam String id, @RequestParam String q) {
        return chat.prompt().user(q)
                .advisors(MessageChatMemoryAdvisor.builder(memory).build())
                .advisors(a -> a.param(ChatMemory.CONVERSATION_ID, id))
                .call().content();
    }
}
