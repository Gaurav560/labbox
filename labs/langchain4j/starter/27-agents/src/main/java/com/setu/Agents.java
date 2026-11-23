package com.setu;

import dev.langchain4j.agentic.AgenticServices;
import dev.langchain4j.model.chat.ChatModel;

/** Setu's agents, and the workflow that joins them. */
public final class Agents {

    private Agents() {
    }

    // TODO (task first_agent): build the classifier agent with AgenticServices.agentBuilder(TopicClassifier.class),
    //   the model, and outputKey("topic"), so its answer is stored in the shared scope as "topic".
    public static TopicClassifier classifier(ChatModel model) {
        return null;
    }

    public static ReplyWriter writer(ChatModel model) {
        return AgenticServices.agentBuilder(ReplyWriter.class)
                .chatModel(model)
                .outputKey("reply")
                .build();
    }

    // TODO (task sequence_workflow): join the two agents: AgenticServices.sequenceBuilder(DeskWorkflow.class),
    //   subAgents(classifier(model), writer(model)), outputKey("reply"), build().
    public static DeskWorkflow desk(ChatModel model) {
        return null;
    }
}
