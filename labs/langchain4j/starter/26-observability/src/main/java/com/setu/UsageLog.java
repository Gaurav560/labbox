package com.setu;

import java.util.concurrent.atomic.AtomicInteger;

import dev.langchain4j.model.chat.listener.ChatModelListener;
import dev.langchain4j.model.chat.listener.ChatModelResponseContext;

/** Listens to every call of a chat model: how many, and how many tokens. */
public class UsageLog implements ChatModelListener {

    final AtomicInteger calls = new AtomicInteger();
    final AtomicInteger inputTokens = new AtomicInteger();
    final AtomicInteger outputTokens = new AtomicInteger();

    // TODO (task usage_listener): count every response. Add 1 to calls, and add the response's input and output
    //   tokens (context.chatResponse().metadata().tokenUsage()) to inputTokens and outputTokens.
    @Override
    public void onResponse(ChatModelResponseContext context) {
    }

    public int calls() {
        return calls.get();
    }

    public int inputTokens() {
        return inputTokens.get();
    }

    public int outputTokens() {
        return outputTokens.get();
    }
}
