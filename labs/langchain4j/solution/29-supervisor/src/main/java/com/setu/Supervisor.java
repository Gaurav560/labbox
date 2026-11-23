package com.setu;

import dev.langchain4j.agentic.AgenticServices;
import dev.langchain4j.agentic.supervisor.SupervisorAgent;
import dev.langchain4j.agentic.supervisor.SupervisorResponseStrategy;
import dev.langchain4j.model.chat.ChatModel;

/** Pure agentic AI: a supervisor plans which agents to call, in which order, to answer a request. */
public final class Supervisor {

    /** House rules for the planner: what it cannot know from the agents' descriptions alone. */
    static final String CONTEXT = "The fare agent returns the fare for ONE adult. When several adults travel, multiply"
            + " that fare by the number of adults, and show the sum in the answer.";

    private Supervisor() {
    }

    public static Specialists.FareAgent fareAgent(ChatModel model) {
        return AgenticServices.agentBuilder(Specialists.FareAgent.class)
                .chatModel(model)
                .tools(new RailTools())
                .outputKey("fare")
                .build();
    }

    public static Specialists.DateAgent dateAgent(ChatModel model) {
        return AgenticServices.agentBuilder(Specialists.DateAgent.class)
                .chatModel(model)
                .tools(new RailTools())
                .outputKey("date")
                .build();
    }

    /** The model plans: which agent, with which arguments, until the request is done. */
    public static SupervisorAgent supervisor(ChatModel model) {
        return AgenticServices.supervisorBuilder()
                .chatModel(model)
                .subAgents(fareAgent(model), dateAgent(model))
                .supervisorContext(CONTEXT)
                .responseStrategy(SupervisorResponseStrategy.SUMMARY)
                .build();
    }
}
