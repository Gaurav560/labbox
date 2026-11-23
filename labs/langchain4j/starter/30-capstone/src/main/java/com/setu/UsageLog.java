package com.setu;

import java.util.concurrent.atomic.AtomicInteger;

import org.springframework.stereotype.Component;

import dev.langchain4j.model.chat.listener.ChatModelListener;
import dev.langchain4j.model.chat.listener.ChatModelResponseContext;

/** Listens to every call of the chat model. A bean, so the starter attaches it to the model. */
@Component
public class UsageLog implements ChatModelListener {

    final AtomicInteger calls = new AtomicInteger();
    final AtomicInteger inputTokens = new AtomicInteger();
    final AtomicInteger outputTokens = new AtomicInteger();

    @Override
    public void onResponse(ChatModelResponseContext context) {
        calls.incrementAndGet();
        var usage = context.chatResponse().metadata().tokenUsage();
        if (usage != null) {
            inputTokens.addAndGet(usage.inputTokenCount());
            outputTokens.addAndGet(usage.outputTokenCount());
        }
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
