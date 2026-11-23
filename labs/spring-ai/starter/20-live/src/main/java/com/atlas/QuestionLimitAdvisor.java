package com.atlas;

import java.util.List;

import org.springframework.ai.chat.client.ChatClientRequest;
import org.springframework.ai.chat.client.ChatClientResponse;
import org.springframework.ai.chat.client.advisor.api.CallAdvisor;
import org.springframework.ai.chat.client.advisor.api.CallAdvisorChain;
import org.springframework.ai.chat.model.ChatResponse;
import org.springframework.ai.chat.model.GuardrailRefusal;
import org.springframework.core.Ordered;

/** A cheap guardrail: questions longer than a limit never reach the model. Long inputs cost money, and most attacks are long. */
public class QuestionLimitAdvisor implements CallAdvisor {

    private final int maxChars;

    public QuestionLimitAdvisor(int maxChars) {
        this.maxChars = maxChars;
    }

    @Override
    public ChatClientResponse adviseCall(ChatClientRequest request, CallAdvisorChain chain) {
        String question = request.prompt().getUserMessage().getText();
        if (question != null && question.length() > maxChars) {
            String text = "That question is too long for me. Please ask it in at most " + maxChars + " characters.";
            ChatResponse refusal = ChatResponse.builder().generations(List.of(GuardrailRefusal.generation(text))).build();
            return ChatClientResponse.builder().chatResponse(refusal).context(request.context()).build();
        }
        return chain.nextCall(request);
    }

    @Override
    public String getName() {
        return "QuestionLimitAdvisor";
    }

    @Override
    public int getOrder() {
        return Ordered.HIGHEST_PRECEDENCE;
    }
}
