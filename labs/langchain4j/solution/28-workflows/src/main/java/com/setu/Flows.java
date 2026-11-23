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

    /** One specialist per topic, chosen by code reading the scope. */
    public static UntypedAgent desks(ChatModel model) {
        return AgenticServices.conditionalBuilder()
                .subAgents(scope -> scope.readState("topic", Topic.OTHER) == Topic.REFUND,
                        agent(Experts.RefundDesk.class, model, "reply"))
                .subAgents(scope -> scope.readState("topic", Topic.OTHER) == Topic.TIMETABLE,
                        agent(Experts.TimetableDesk.class, model, "reply"))
                .subAgents(scope -> {
                            Topic t = scope.readState("topic", Topic.OTHER);
                            return t != Topic.REFUND && t != Topic.TIMETABLE;
                        },
                        agent(Experts.GeneralDesk.class, model, "reply"))
                .build();
    }

    /** Score, edit, score again: at most three rounds, and out as soon as the score is good. */
    public static UntypedAgent reviewLoop(ChatModel model) {
        return AgenticServices.loopBuilder()
                .subAgents(agent(Review.ReplyScorer.class, model, "score"), agent(Review.ReplyEditor.class, model, "reply"))
                .maxIterations(3)
                .exitCondition(scope -> scope.readState("score", 0.0) >= 0.8)
                .build();
    }

    /** The whole desk: classify, route to a specialist, then review. */
    public static DeskWorkflow desk(ChatModel model) {
        return AgenticServices.sequenceBuilder(DeskWorkflow.class)
                .subAgents(agent(TopicClassifier.class, model, "topic"), desks(model), reviewLoop(model))
                .outputKey("reply")
                .build();
    }
}
