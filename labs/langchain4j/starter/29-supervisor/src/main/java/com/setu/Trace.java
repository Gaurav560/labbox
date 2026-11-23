package com.setu;

import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.chat.listener.ChatModelListener;
import dev.langchain4j.model.chat.listener.ChatModelRequestContext;

/** Prints the first words of each prompt, so you can see which agent is working. */
public class Trace implements ChatModelListener {

    @Override
    public void onRequest(ChatModelRequestContext context) {
        var messages = context.chatRequest().messages();
        if (messages.get(messages.size() - 1) instanceof UserMessage u) {
            String text = u.singleText().replace("\n", " ");
            System.out.println("  [model call] " + (text.length() > 60 ? text.substring(0, 60) + "..." : text));
        }
    }
}
