package com.setu.check;

import java.util.List;
import java.util.Map;
import java.util.concurrent.CopyOnWriteArrayList;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;

import com.setu.DeskWorkflow;
import com.setu.Flows;
import com.setu.Models;
import com.setu.TopicClassifier;

import dev.langchain4j.agentic.AgenticServices;
import dev.langchain4j.agentic.UntypedAgent;
import dev.langchain4j.model.chat.ChatModel;

class Ch28Check {

    static final FakeOpenAi FAKE = new FakeOpenAi();

    @AfterAll
    static void stop() { FAKE.stop(); }

    static ChatModel model() {
        return Models.chatModel(FAKE.baseUrl(), "k");
    }

    /** Classify as the given topic; each desk answers with its own name, so the check sees which desk ran. */
    static String route(String topic) {
        FAKE.reset();
        FAKE.script = b -> {
            if (b.contains("Which team should handle")) return FakeOpenAi.Reply.text(topic);
            if (b.contains("You handle refunds")) return FakeOpenAi.Reply.text("refund desk");
            if (b.contains("You handle timetable")) return FakeOpenAi.Reply.text("timetable desk");
            if (b.contains("Apologise once")) return FakeOpenAi.Reply.text("general desk");
            return FakeOpenAi.Reply.text("?");
        };
        UntypedAgent desks = Flows.desks(model());
        DeskWorkflow flow = AgenticServices.sequenceBuilder(DeskWorkflow.class)
                .subAgents(AgenticServices.agentBuilder(TopicClassifier.class).chatModel(model()).outputKey("topic").build(), desks)
                .outputKey("reply").build();
        return flow.handle("a message");
    }

    @Test
    void conditionalRoute() {
        R.task("conditional_route", () -> {
            if (Flows.desks(model()) == null) {
                R.fail("conditional_route", "Flows.desks(model) returned null. Build it with AgenticServices.conditionalBuilder(), one .subAgents(condition, desk) per desk, and .build().");
                return;
            }
            String[][] cases = {{"REFUND", "refund desk"}, {"TIMETABLE", "timetable desk"}, {"COMPLAINT", "general desk"}, {"OTHER", "general desk"}};
            for (String[] c : cases) {
                String got = route(c[0]);
                int deskCalls = FAKE.chatRequests.size() - 1;
                if (deskCalls != 1) {
                    R.fail("conditional_route", "For a " + c[0] + " message exactly one desk should answer, but " + deskCalls + " did. Make the conditions exclusive: REFUND, TIMETABLE, and neither.",
                            "1 desk", deskCalls + " desks");
                    return;
                }
                if (!c[1].equals(got)) {
                    R.fail("conditional_route", "A " + c[0] + " message went to the wrong desk. Check each condition: scope.readState(\"topic\", Topic.OTHER) == Topic.REFUND, and so on.", c[1], String.valueOf(got));
                    return;
                }
            }
            R.pass("conditional_route", "Code chose the desk, not the model: REFUND, TIMETABLE and everything else each went to their own agent.");
        });
    }

    @Test
    void reviewLoop() {
        R.task("review_loop", () -> {
            UntypedAgent loop = Flows.reviewLoop(model());
            if (loop == null) {
                R.fail("review_loop", "Flows.reviewLoop(model) returned null. Build it with AgenticServices.loopBuilder(), .subAgents(scorer, editor), .maxIterations(3), .exitCondition(...) and .build().");
                return;
            }
            List<String> calls = new CopyOnWriteArrayList<>();
            FAKE.reset();
            FAKE.script = b -> {
                if (b.contains("Score this reply")) {
                    calls.add("score");
                    return FakeOpenAi.Reply.text(calls.stream().filter("score"::equals).count() == 1 ? "0.3" : "0.9");
                }
                calls.add("edit");
                return FakeOpenAi.Reply.text("We are sorry. Your refund will reach you in 5 working days.");
            };
            var res = loop.invokeWithAgenticScope(Map.of("reply", "Hello!!! So sorry!!! We will refund you everything immediately, I promise, today, now."));
            String reply = String.valueOf(res.agenticScope().readState("reply"));
            if (!List.of("score", "edit", "score").equals(calls)) {
                R.fail("review_loop", "Score 0.3, then an edit, then 0.9 should stop the loop. Put the scorer first and the editor second, and exit when scope.readState(\"score\", 0.0) >= 0.8.",
                        "[score, edit, score]", calls.toString());
                return;
            }
            if (!reply.startsWith("We are sorry.")) {
                R.fail("review_loop", "The editor's new reply should replace \"reply\" in the scope: build it with outputKey \"reply\".", "We are sorry. Your refund...", reply);
                return;
            }
            calls.clear();
            FAKE.script = b -> {
                calls.add(b.contains("Score this reply") ? "score" : "edit");
                return FakeOpenAi.Reply.text(b.contains("Score this reply") ? "0.2" : "Still not good.");
            };
            loop.invokeWithAgenticScope(Map.of("reply", "Bad reply"));
            if (calls.size() != 6) {
                R.fail("review_loop", "A reply that never scores 0.8 should stop after 3 rounds (6 model calls): set .maxIterations(3).", "6 calls", calls.size() + " calls");
                return;
            }
            R.pass("review_loop", "Score, edit, score: out as soon as it is good, and never more than three rounds, so the bill has a ceiling.");
        });
    }
}
