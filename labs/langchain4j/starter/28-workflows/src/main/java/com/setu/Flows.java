package com.setu;

import dev.langchain4j.agentic.AgenticServices;
import dev.langchain4j.agentic.UntypedAgent;
import dev.langchain4j.model.chat.ChatModel;

/** Workflows: agents joined by code you can read, test and predict. */
public final class Flows {

    private Flows() {
    }

    static <T> T agent(Class<T> type, ChatModel model, String outputKey) {
        return AgenticServices.agentBuilder(type).chatModel(model).outputKey(outputKey).build();
    }

    // TODO (task conditional_route): send each message to one desk, by the "topic" in the scope:
    //   AgenticServices.conditionalBuilder()
    //     .subAgents(scope -> scope.readState("topic", Topic.OTHER) == Topic.REFUND, the RefundDesk agent)
    //     .subAgents(scope -> scope.readState("topic", Topic.OTHER) == Topic.TIMETABLE, the TimetableDesk agent)
    //     .subAgents(scope -> the topic is neither, the GeneralDesk agent)
    //   Build each desk with agent(Experts.RefundDesk.class, model, "reply"), and so on. Then build().
    public static UntypedAgent desks(ChatModel model) {
        return null;
    }

    // TODO (task review_loop): improve the reply until it scores 0.8: AgenticServices.loopBuilder()
    //   .subAgents(agent(Review.ReplyScorer.class, model, "score"), agent(Review.ReplyEditor.class, model, "reply"))
    //   .maxIterations(3).exitCondition(scope -> scope.readState("score", 0.0) >= 0.8).build()
    public static UntypedAgent reviewLoop(ChatModel model) {
        return null;
    }

    /** The whole desk: classify, route to a specialist, then review. */
    public static DeskWorkflow desk(ChatModel model) {
        return AgenticServices.sequenceBuilder(DeskWorkflow.class)
                .subAgents(agent(TopicClassifier.class, model, "topic"), desks(model), reviewLoop(model))
                .outputKey("reply")
                .build();
    }
}
