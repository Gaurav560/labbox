package com.atlas;

import java.util.Map;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** Two workflows from "Building Effective Agents": routing, and evaluator-optimizer. */
@RestController
public class AgentController {

    /** Which desk a question belongs to. */
    public enum Desk { EXHIBITS, VISIT, BOOKING }

    public record Routing(Desk desk) {}

    public record Routed(Desk desk, String answer) {}

    /** The reviewer's verdict on a draft. */
    public record Review(boolean approved, String feedback) {}

    /** A finished label, and how many drafts it took. */
    public record Label(String text, int drafts) {}

    static final String ROUTER = """
            You sort visitor questions for the Deccan Science Museum in Pune into one desk.
            EXHIBITS: science, and the museum's exhibits. VISIT: opening hours, tickets, directions, facilities.
            BOOKING: booking seats for planetarium shows.
            """;

    static final Map<Desk, String> DESKS = Map.of(
            Desk.EXHIBITS, """
                    You are Atlas, the science explainer of the Deccan Science Museum in Pune.
                    Explain in at most three short sentences, for a curious ten-year-old.
                    """,
            Desk.VISIT, """
                    You are Atlas at the front desk of the Deccan Science Museum in Pune. The facts:
                    open Tuesday to Sunday, 10:00 to 18:00, last entry 17:00, closed on Mondays.
                    Tickets: 120 rupees for adults, 60 for children aged 5 to 15 and students, free under 5.
                    Planetarium shows: 80 rupees extra. Lifts in every gallery; lockers and wheelchairs free.
                    Answer in at most two sentences, only from these facts.
                    """,
            Desk.BOOKING, """
                    You are Atlas at the planetarium desk of the Deccan Science Museum in Pune.
                    Shows at 11:00, 14:00 and 16:00, Tuesday to Sunday. You cannot book seats yourself:
                    tell the visitor to book at atlas.deccanscience.example/book or at the ticket counter.
                    Answer in at most two sentences.
                    """);

    static final String WRITER = "You write exhibit labels for the Deccan Science Museum in Pune.";

    static final String REVIEWER = """
            You review exhibit labels for children. Approve a label only if it follows every rule.
            If it does not, say in one sentence what to change.
            """;

    static final String RULES = "at most 40 words; only words a nine-year-old knows; "
            + "end with a question that makes the reader look closer at the exhibit";

    private final ChatClient chat;

    public AgentController(ChatClient.Builder builder) {
        this.chat = builder.build();
    }

    /** GET /agent/route?q=... first decide which desk should answer, then answer as that desk. */
    @GetMapping("/agent/route")
    public Routed route(@RequestParam String q) {
        // TODO (task route_question): ask the model which Desk fits (ROUTER prompt, as Routing), then answer with DESKS.get(desk).
        return new Routed(Desk.EXHIBITS, chat.prompt().user(q).call().content());
    }

    /** GET /agent/label?exhibit=... write a label for children, then review and rewrite it, at most 3 drafts. */
    @GetMapping("/agent/label")
    public Label label(@RequestParam String exhibit) {
        String draft = chat.prompt()
                .system(WRITER)
                .user("Write a label for this exhibit: " + exhibit + ". Rules: " + RULES)
                .call()
                .content();
        // TODO (task improve_loop): review the draft (REVIEWER, RULES, as a Review); if not approved, rewrite it with the
        // feedback and review again. Stop when approved or after 3 drafts.
        return new Label(draft, 1);
    }
}
