package com.atlas;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.messages.AssistantMessage;
import org.springframework.ai.chat.messages.Message;
import org.springframework.ai.chat.messages.SystemMessage;
import org.springframework.ai.chat.messages.UserMessage;
import org.springframework.ai.chat.model.ChatResponse;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.ai.model.tool.ToolCallDecision;
import org.springframework.ai.model.tool.ToolCallDecisions;
import org.springframework.ai.model.tool.ToolCallingChatOptions;
import org.springframework.ai.model.tool.ToolCallingManager;
import org.springframework.ai.model.tool.ToolExecutionResult;
import org.springframework.ai.support.ToolCallbacks;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** Atlas can book planetarium seats, but only after the visitor says yes. */
@RestController
public class BookingController {

    static final String SYSTEM = """
            You are Atlas, the friendly visitor guide of the Deccan Science Museum in Pune.
            Answer in at most three short sentences, in plain, simple words.
            You can book planetarium seats with the bookSeats tool when a visitor asks you to.
            """;

    /** A tool call waiting for the visitor's decision. */
    public record PendingCall(String key, String tool, String arguments) {}

    /** Either an answer, or calls waiting for a yes or no (with the id to confirm them). */
    public record Reply(String answer, String pendingId, List<PendingCall> pending) {}

    /** What the app keeps while a reply waits: the conversation the model answered, and its reply. */
    private record Paused(Prompt prompt, ChatResponse reply) {}

    private final ChatClient chat;
    private final BookingTools tools;
    private final ToolCallingManager toolCallingManager;
    private final Map<String, Paused> paused = new ConcurrentHashMap<>();

    public BookingController(ChatClient.Builder builder, BookingTools tools, ToolCallingManager toolCallingManager) {
        this.chat = builder.build();
        this.tools = tools;
        this.toolCallingManager = toolCallingManager;
    }

    /** GET /book?visitor=ria&q=Book two seats for the 16:00 show on 2026-11-28 */
    @GetMapping("/book")
    public Reply book(@RequestParam String visitor, @RequestParam String q) {
        List<Message> conversation = List.of(new SystemMessage(SYSTEM), new UserMessage(q));
        Map<String, Object> context = Map.of("visitor", visitor);
        ChatResponse reply = chat.prompt()
                .messages(conversation)
                .tools(tools)
                .toolContext(context)
                .call()
                .chatResponse();
        List<String> awaiting = ToolCallDecisions.awaitingDecision(reply);
        if (awaiting.isEmpty()) {
            return new Reply(reply.getResult().getOutput().getText(), null, List.of());
        }
        // The model asked for a tool that needs a yes: nothing has run. Keep the conversation and the reply.
        AssistantMessage message = reply.getResult().getOutput();
        List<String> keys = ToolCallDecisions.toolCallKeys(message);
        List<PendingCall> calls = new ArrayList<>();
        for (int i = 0; i < keys.size(); i++) {
            AssistantMessage.ToolCall call = message.getToolCalls().get(i);
            calls.add(new PendingCall(keys.get(i), call.name(), call.arguments()));
        }
        String id = UUID.randomUUID().toString();
        Prompt prompt = new Prompt(conversation, ToolCallingChatOptions.builder()
                .toolCallbacks(ToolCallbacks.from(tools))
                .toolContext(context)
                .build());
        paused.put(id, new Paused(prompt, reply));
        return new Reply(null, id, calls);
    }

    /** POST /book/{id}/confirm?yes=true runs the waiting calls (or refuses them), then lets the model answer. */
    @PostMapping("/book/{id}/confirm")
    public Reply confirm(@PathVariable String id, @RequestParam boolean yes) {
        Paused p = paused.remove(id);
        if (p == null) {
            return new Reply("Nothing is waiting with that id.", null, List.of());
        }
        List<ToolCallDecision> decisions = new ArrayList<>();
        for (String key : ToolCallDecisions.toolCallKeys(p.reply().getResult().getOutput())) {
            decisions.add(yes ? ToolCallDecision.allow(key) : ToolCallDecision.deny(key, "The visitor chose not to book. Nothing was booked. Say only that, kindly, and offer more help."));
        }
        ToolExecutionResult result = toolCallingManager.executeToolCalls(p.prompt(), p.reply(), new ToolCallDecisions(decisions));
        String answer = chat.prompt()
                .messages(result.conversationHistory())
                .call()
                .content();
        return new Reply(answer, null, List.of());
    }
}
