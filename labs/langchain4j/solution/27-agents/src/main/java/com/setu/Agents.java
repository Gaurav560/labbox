package com.setu;

import dev.langchain4j.agentic.AgenticServices;
import dev.langchain4j.model.chat.ChatModel;

/** Setu's agents, and the workflow that joins them. */
public final class Agents {

    private Agents() {
    }

    public static TopicClassifier classifier(ChatModel model) {
        return AgenticServices.agentBuilder(TopicClassifier.class)
                .chatModel(model)
                .outputKey("topic")
                .build();
    }

    public static ReplyWriter writer(ChatModel model) {
        return AgenticServices.agentBuilder(ReplyWriter.class)
                .chatModel(model)
                .outputKey("reply")
                .build();
    }

    /** First classify, then write: the writer reads "topic" from the scope the classifier wrote. */
    public static DeskWorkflow desk(ChatModel model) {
        return AgenticServices.sequenceBuilder(DeskWorkflow.class)
                .subAgents(classifier(model), writer(model))
                .outputKey("reply")
                .build();
    }
}
