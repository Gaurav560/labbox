package com.setu;

import dev.langchain4j.data.message.SystemMessage;
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.chat.response.ChatResponse;
import dev.langchain4j.model.openai.OpenAiChatModel;

/** Chapter 12: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) {
        ChatModel model = OpenAiChatModel.builder().baseUrl(System.getenv("OPENAI_BASE_URL"))
                .apiKey(System.getenv("OPENAI_API_KEY")).modelName("ai-chat").build();
        String system = "You are Setu, the help desk assistant of Sahyadri Rail. Answer in at most three short sentences.";
        for (String q : new String[] {"Hi!", "Explain in detail how a train climbs a steep ghat section."}) {
            ChatResponse r = model.chat(SystemMessage.from(system), UserMessage.from(q));
            Bill.Usage u = Bill.usage(r);
            System.out.println("Q: " + q);
            System.out.println("  model " + r.metadata().modelName() + ", finish " + r.metadata().finishReason()
                    + ", " + u.inputTokens() + " in, " + u.outputTokens() + " out, $" + String.format("%.6f", Bill.dollars(u)));
        }
        Bill.Usage day = new Bill.Usage(400 * 180, 400 * 60);
        System.out.printf("%n400 questions a day, about 180 tokens in and 60 out each: $%.4f a day, $%.2f a year%n",
                Bill.dollars(day), Bill.dollars(day) * 365);
    }
}
