package com.atlas;

import java.util.concurrent.atomic.AtomicLong;

import org.springframework.ai.chat.client.ChatClientRequest;
import org.springframework.ai.chat.client.ChatClientResponse;
import org.springframework.ai.chat.client.advisor.api.CallAdvisor;
import org.springframework.ai.chat.client.advisor.api.CallAdvisorChain;
import org.springframework.ai.chat.metadata.Usage;
import org.springframework.stereotype.Component;

/** Counts every model call Atlas makes, and the tokens they use: a meter for the finance office. */
@Component
public class UsageAdvisor implements CallAdvisor {

    private final AtomicLong calls = new AtomicLong();
    private final AtomicLong tokens = new AtomicLong();

    @Override
    public String getName() {
        return "UsageAdvisor";
    }

    @Override
    public int getOrder() {
        return 0;
    }

    @Override
    public ChatClientResponse adviseCall(ChatClientRequest request, CallAdvisorChain chain) {
        ChatClientResponse response = chain.nextCall(request);
        calls.incrementAndGet();
        Usage usage = response.chatResponse().getMetadata().getUsage();
        tokens.addAndGet(usage.getTotalTokens());
        return response;
    }

    public long calls() {
        return calls.get();
    }

    public long tokens() {
        return tokens.get();
    }
}
