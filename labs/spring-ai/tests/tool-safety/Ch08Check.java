package com.atlas.check;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;

import com.atlas.BookingService;

/** Chapter 8: a tool that changes things waits for a yes, and acts for the right visitor. */
@SpringBootTest
@AutoConfigureMockMvc
class Ch08Check {
    static final FakeOpenAi AI = new FakeOpenAi();
    static final JsonMapper JSON = JsonMapper.builder().build();

    @DynamicPropertySource
    static void ai(DynamicPropertyRegistry r) {
        r.add("spring.ai.openai.base-url", AI::baseUrl);
        r.add("spring.ai.openai.api-key", () -> "check-key");
    }

    @AfterAll
    static void stop() {
        AI.stop();
    }

    @Autowired
    MockMvc mvc;

    @Autowired
    BookingService bookings;

    /** The fake model books two seats for the 16:00 show, naming the visitor "Sam" (it may well guess a name). */
    static void bookTwoSeats() {
        AI.script = b -> {
            if (b.contains("\"role\":\"tool\"")) return FakeOpenAi.Reply.text("All done. Enjoy the show!");
            return FakeOpenAi.Reply.tool("bookSeats", "{\"date\":\"2026-11-28\",\"time\":\"16:00\",\"seats\":2,\"visitorName\":\"Sam\"}");
        };
    }

    JsonNode book(String visitor) throws Exception {
        String body = mvc.perform(get("/book").param("visitor", visitor).param("q", "Book two seats for the 16:00 show on 2026-11-28."))
                .andReturn().getResponse().getContentAsString();
        return JSON.readTree(body);
    }

    JsonNode confirm(String id, boolean yes) throws Exception {
        return JSON.readTree(mvc.perform(post("/book/" + id + "/confirm").param("yes", String.valueOf(yes))).andReturn().getResponse().getContentAsString());
    }

    @Test
    void confirmBooking() {
        R.task("confirm_booking", () -> {
            AI.reset();
            bookTwoSeats();
            int before = bookings.bookings().size();
            JsonNode r = book("ria");
            if (bookings.bookings().size() > before) {
                R.fail("confirm_booking", "the seats were booked the moment the model asked, without the visitor's yes. Add requiresConfirmation = true to the bookSeats @Tool.");
                return;
            }
            String id = r.path("pendingId").asString("");
            if (id.isEmpty() || !r.path("pending").toString().contains("bookSeats")) {
                R.fail("confirm_booking", "GET /book should answer with the call that waits for a decision.", "pendingId and a pending bookSeats call", r.toString());
                return;
            }
            JsonNode no = confirm(id, false);
            if (bookings.bookings().size() > before) {
                R.fail("confirm_booking", "the visitor said no, but the seats were booked anyway.");
                return;
            }
            AI.reset();
            bookTwoSeats();
            JsonNode again = book("ria");
            confirm(again.path("pendingId").asString(""), true);
            if (bookings.bookings().size() != before + 1) {
                R.fail("confirm_booking", "after the visitor's yes, the booking should be made.", (before + 1) + " bookings", bookings.bookings().size() + " bookings");
                return;
            }
            R.pass("confirm_booking", "The booking waited for a yes: a no booked nothing, a yes booked two seats. The model can ask; only the visitor decides.");
        });
    }

    @Test
    void toolContext() {
        R.task("tool_context", () -> {
            AI.reset();
            bookTwoSeats();
            int before = bookings.bookings().size();
            JsonNode r = book("ria");
            String id = r.path("pendingId").asString("");
            if (!id.isEmpty()) confirm(id, true);
            if (bookings.bookings().size() == before) {
                R.fail("tool_context", "no booking was made at all, so there is no visitor to check. Make the booking work first.");
                return;
            }
            String who = bookings.bookings().get(bookings.bookings().size() - 1).visitor();
            if (!"ria".equals(who)) {
                R.fail("tool_context", "the model chose whose booking it was (it said Sam). Take the visitor from the tool context: add a ToolContext parameter and read context.getContext().get(\"visitor\"), and drop the visitorName parameter.", "ria", String.valueOf(who));
                return;
            }
            JsonNode first = AI.chat(0);
            if (first.toString().contains("visitorName")) {
                R.fail("tool_context", "the booking is right, but the tool still asks the model for a visitorName. Remove that parameter: the model should not even be able to try.");
                return;
            }
            R.pass("tool_context", "The model asked for Sam, and the booking went to Ria: the visitor comes from your app, through the tool context, and the model never sees it.");
        });
    }
}
