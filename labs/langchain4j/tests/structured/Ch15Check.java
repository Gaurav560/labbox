package com.setu.check;

import java.lang.reflect.Method;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;

import com.setu.Models;
import com.setu.Reader;
import com.setu.Topic;
import com.setu.TripRequest;

import dev.langchain4j.service.AiServices;
import tools.jackson.databind.JsonNode;

class Ch15Check {

    static final FakeOpenAi FAKE = new FakeOpenAi();

    @AfterAll
    static void stop() { FAKE.stop(); }

    static Reader reader() {
        return AiServices.create(Reader.class, Models.structuredModel(FAKE.baseUrl(), "k"));
    }

    @Test
    void extractTrip() {
        R.task("extract_trip", () -> {
            Method m = Reader.class.getMethod("trip", String.class);
            if (m.getReturnType() != TripRequest.class) {
                R.fail("extract_trip", "Reader.trip still returns " + m.getReturnType().getSimpleName() + ". Change its return type to TripRequest; LangChain4j does the rest.", "TripRequest", m.getReturnType().getSimpleName());
                return;
            }
            FAKE.reset();
            FAKE.script = b -> FakeOpenAi.Reply.text("{\"from\":\"Pune\",\"to\":\"Karjat\",\"date\":\"2026-11-28\",\"passengers\":3}");
            Object got = m.invoke(reader(), "3 tickets Pune to Karjat on Saturday");
            JsonNode req = FAKE.chat(-1);
            JsonNode schema = req.path("response_format").path("json_schema");
            if (!"TripRequest".equals(schema.path("name").asString())) {
                R.fail("extract_trip", "The request did not carry TripRequest's JSON schema. Keep the method on the Reader interface, returning TripRequest.");
                return;
            }
            if (!(got instanceof TripRequest t) || !"Karjat".equals(t.to()) || t.passengers() != 3) {
                R.fail("extract_trip", "trip(...) should return the TripRequest LangChain4j parsed from the model's JSON.", "TripRequest[from=Pune, to=Karjat, date=2026-11-28, passengers=3]", String.valueOf(got));
                return;
            }
            R.pass("extract_trip", "A record in, a record out: the schema went to the model, the JSON came back as a typed Java object.");
        });
    }

    @Test
    void classifyTopic() {
        R.task("classify_topic", () -> {
            Method m;
            try {
                m = Reader.class.getMethod("topic", String.class);
            } catch (NoSuchMethodException e) {
                R.fail("classify_topic", "Reader has no method topic(String). Add: Topic topic(String message), with @UserMessage(\"Which team should handle this passenger message? {{it}}\").");
                return;
            }
            if (m.getReturnType() != Topic.class) {
                R.fail("classify_topic", "topic(...) should return the Topic enum, so the answer can only be one of its values.", "Topic", m.getReturnType().getSimpleName());
                return;
            }
            FAKE.reset();
            FAKE.script = b -> FakeOpenAi.Reply.text("{\"value\":\"REFUND\"}");
            Object got = m.invoke(reader(), "I cancelled yesterday, where is my money?");
            JsonNode req = FAKE.chat(-1);
            String user = FakeOpenAi.texts(req, "user").isEmpty() ? "" : FakeOpenAi.texts(req, "user").get(0);
            if (!user.equals("Which team should handle this passenger message? I cancelled yesterday, where is my money?")) {
                R.fail("classify_topic", "Use the @UserMessage text from the TODO, with {{it}} for the message.", "Which team should handle this passenger message? I cancelled...", user);
                return;
            }
            if (got != Topic.REFUND) {
                R.fail("classify_topic", "topic(...) should return the enum value the model chose.", "REFUND", String.valueOf(got));
                return;
            }
            R.pass("classify_topic", "An enum as the return type: the model can only answer with one of your six values, and your code can switch on it.");
        });
    }
}
