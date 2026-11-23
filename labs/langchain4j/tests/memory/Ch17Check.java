package com.setu.check;

import java.util.List;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;

import com.setu.Assistant;
import com.setu.Memories;
import com.setu.PassengerDesk;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import tools.jackson.databind.JsonNode;

class Ch17Check {

    static final FakeOpenAi FAKE = new FakeOpenAi();

    @AfterAll
    static void stop() { FAKE.stop(); }

    static ChatModel model() {
        return OpenAiChatModel.builder().baseUrl(FAKE.baseUrl()).apiKey("k").modelName("ai-chat").build();
    }

    @Test
    void windowMemory() {
        R.task("window_memory", () -> {
            FAKE.reset();
            FAKE.script = b -> FakeOpenAi.Reply.text("Noted.");
            Assistant setu = Memories.assistant(model());
            setu.chat("My name is Meera.");
            setu.chat("What is my name?");
            JsonNode req = FAKE.chat(-1);
            List<String> users = FakeOpenAi.texts(req, "user");
            if (!users.contains("My name is Meera.")) {
                R.fail("window_memory", "The second request did not include the first message, so Setu forgot it. Build the assistant with AiServices.builder(Assistant.class), .chatModel(model) and .chatMemory(MessageWindowChatMemory.withMaxMessages(10)).",
                        "[My name is Meera., What is my name?]", users.toString());
                return;
            }
            if (!FakeOpenAi.texts(req, "assistant").contains("Noted.")) {
                R.fail("window_memory", "The history should include Setu's own earlier answer too: the memory keeps both sides.");
                return;
            }
            for (int i = 0; i < 12; i++) setu.chat("Message " + i);
            int sent = FAKE.chat(-1).path("messages").size();
            if (sent > 11) {
                R.fail("window_memory", "The memory keeps growing: after 14 questions the request had " + sent + " messages. Use MessageWindowChatMemory.withMaxMessages(10).", "at most 10 messages (plus the system message)", String.valueOf(sent));
                return;
            }
            R.pass("window_memory", "Setu remembers the conversation, and the window keeps it from growing forever.");
        });
    }

    @Test
    void memoryPerPassenger() {
        R.task("memory_per_passenger", () -> {
            FAKE.reset();
            FAKE.script = b -> FakeOpenAi.Reply.text("Noted.");
            PassengerDesk desk;
            try {
                desk = Memories.desk(model());
                desk.chat("ravi", "I lost my umbrella.");
                desk.chat("asha", "I want two seats.");
                desk.chat("ravi", "What did I lose?");
            } catch (RuntimeException e) {
                R.fail("memory_per_passenger", "The desk could not answer: " + String.valueOf(e.getMessage()).lines().findFirst().orElse("")
                        + ". A method with @MemoryId needs a chatMemoryProvider on the builder: id -> MessageWindowChatMemory.builder().id(id).maxMessages(10).build().");
                return;
            }
            List<String> users = FakeOpenAi.texts(FAKE.chat(-1), "user");
            if (!users.contains("I lost my umbrella.")) {
                R.fail("memory_per_passenger", "Ravi's second question was sent without his first: give the builder a chatMemoryProvider, so each passenger has a memory.", "[I lost my umbrella., What did I lose?]", users.toString());
                return;
            }
            if (users.contains("I want two seats.")) {
                R.fail("memory_per_passenger", "Ravi's request contains Asha's message: the memories are shared. The provider must make a separate memory for each id.", "[I lost my umbrella., What did I lose?]", users.toString());
                return;
            }
            R.pass("memory_per_passenger", "One AI Service, a separate conversation per passenger, chosen by @MemoryId.");
        });
    }
}
