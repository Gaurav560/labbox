package com.setu;

import java.util.Map;

import dev.langchain4j.model.chat.ChatModel;

/** Chapter 28: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) {
        ChatModel model = Models.chatModel(System.getenv("OPENAI_BASE_URL"), System.getenv("OPENAI_API_KEY"), new Trace());
        DeskWorkflow desk = Flows.desk(model);
        for (String m : new String[] {"I cancelled my Ratnagiri ticket 3 days before, how much do I get back?",
                "When does the Monsoon Mail reach Karjat?"}) {
            System.out.println("\n> " + m);
            System.out.println(desk.handle(m));
        }
        String rambling = "Dear passenger!!! We are SO sorry!!! Your money will definitely be back today, we promise, and we"
                + " will also give you a free ticket, and our manager will call you personally tonight.";
        System.out.println("\n> the review loop alone, on a bad reply:");
        var result = Flows.reviewLoop(model).invokeWithAgenticScope(Map.of("reply", rambling));
        System.out.println("score " + result.agenticScope().readState("score") + ": " + result.agenticScope().readState("reply"));
    }
}
