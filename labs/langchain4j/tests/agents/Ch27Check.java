package com.setu.check;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;

import com.setu.Agents;
import com.setu.DeskWorkflow;
import com.setu.Models;
import com.setu.Topic;
import com.setu.TopicClassifier;

import dev.langchain4j.agentic.AgenticServices;
import dev.langchain4j.model.chat.ChatModel;

class Ch27Check {

    static final FakeOpenAi FAKE = new FakeOpenAi();

    @AfterAll
    static void stop() { FAKE.stop(); }

    static ChatModel model() {
        return Models.chatModel(FAKE.baseUrl(), "k");
    }

    /** The classifier is asked "Which team...?"; the writer gets everything else. */
    static void script() {
        FAKE.reset();
        FAKE.script = b -> b.contains("Which team should handle")
                ? FakeOpenAi.Reply.text("COMPLAINT")
                : FakeOpenAi.Reply.text("Sorry about the delay. Our complaints team will reply within a day.");
    }

    @Test
    void firstAgent() {
        R.task("first_agent", () -> {
            script();
            TopicClassifier classifier = Agents.classifier(model());
            if (classifier == null) {
                R.fail("first_agent", "Agents.classifier(model) returned null. Build it with AgenticServices.agentBuilder(TopicClassifier.class), .chatModel(model), .outputKey(\"topic\") and .build().");
                return;
            }
            Topic got = classifier.classify("The train was late again!");
            if (got != Topic.COMPLAINT) {
                R.fail("first_agent", "The model answered COMPLAINT, so classify(...) should return Topic.COMPLAINT.", "COMPLAINT", String.valueOf(got));
                return;
            }
            // Join it with the (given) writer: the writer reads {{topic}}, so this works only if the classifier stores "topic".
            DeskWorkflow pair = AgenticServices.sequenceBuilder(DeskWorkflow.class)
                    .subAgents(Agents.classifier(model()), Agents.writer(model())).outputKey("reply").build();
            script();
            try {
                pair.handle("The train was late again!");
            } catch (RuntimeException e) {
                R.fail("first_agent", "The classifier works alone, but the next agent could not find \"topic\" in the shared scope. Add .outputKey(\"topic\") to the classifier's builder.");
                return;
            }
            if (FAKE.chatRequests.size() < 2 || !FAKE.chatRequests.get(1).contains("COMPLAINT team")) {
                R.fail("first_agent", "The writer did not receive the topic. Add .outputKey(\"topic\") to the classifier's builder.");
                return;
            }
            R.pass("first_agent", "An agent: an AI Service with a description, whose answer lands in the shared scope as \"topic\".");
        });
    }

    @Test
    void sequenceWorkflow() {
        R.task("sequence_workflow", () -> {
            DeskWorkflow desk = Agents.desk(model());
            if (desk == null) {
                R.fail("sequence_workflow", "Agents.desk(model) returned null. Build it with AgenticServices.sequenceBuilder(DeskWorkflow.class), .subAgents(classifier(model), writer(model)), .outputKey(\"reply\") and .build().");
                return;
            }
            script();
            String got = desk.handle("The 7:15 was 40 minutes late!");
            if (FAKE.chatRequests.size() != 2 || !FAKE.chatRequests.get(0).contains("Which team should handle")) {
                R.fail("sequence_workflow", "The desk should call the classifier first, then the writer: subAgents(classifier(model), writer(model)), in that order.",
                        "2 model calls, classifier first", FAKE.chatRequests.size() + " model calls");
                return;
            }
            if (!"Sorry about the delay. Our complaints team will reply within a day.".equals(got)) {
                R.fail("sequence_workflow", "handle(...) should return the writer's reply: give the sequence .outputKey(\"reply\").",
                        "Sorry about the delay. Our complaints team will reply within a day.", String.valueOf(got));
                return;
            }
            R.pass("sequence_workflow", "Two agents, one workflow: the classifier wrote \"topic\", the writer read it, and you called one method.");
        });
    }
}
