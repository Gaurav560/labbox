package com.setu;

import dev.langchain4j.data.message.SystemMessage;
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel;

/** Chapter 11: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) throws Exception {
        ChatModel model = OpenAiChatModel.builder().baseUrl(System.getenv("OPENAI_BASE_URL"))
                .apiKey(System.getenv("OPENAI_API_KEY")).modelName("ai-chat").temperature(0.0).build();
        String[] questions = {"What time does the Ghat Express leave Pune?", "How much is a ticket from Pune to Karjat?",
                "Does the Konkan Breeze run on Tuesdays?"};
        for (String q : questions) {
            System.out.println("Q: " + q);
            String plain = model.chat(SystemMessage.from(Honest.SYSTEM), UserMessage.from(q)).aiMessage().text();
            System.out.println("  no facts:   " + plain);
            System.out.println("  with facts: " + Honest.ask(model, q));
        }
        System.out.println("Q: Is there wifi on the Monsoon Mail?");
        System.out.println("  with facts: " + Honest.ask(model, "Is there wifi on the Monsoon Mail?"));
    }
}
