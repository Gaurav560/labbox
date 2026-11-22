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
        // TODO (task usage_advisor): pass the request on down the chain, then count the call and its total tokens.
        return chain.nextCall(request);
    }

    public long calls() {
        return calls.get();
    }

    public long tokens() {
        return tokens.get();
    }
}
