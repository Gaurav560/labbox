package com.atlas;

import org.springframework.ai.chat.model.ToolContext;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Component;

/** A tool that changes something: it books planetarium seats. */
@Component
public class BookingTools {

    private final BookingService bookings;

    public BookingTools(BookingService bookings) {
        this.bookings = bookings;
    }

    // TODO (task confirm_booking): booking must wait for the visitor's yes. Mark this tool as needing confirmation.
    // TODO (task tool_context): who books should come from the app (the tool context), never from the model.
    @Tool(description = "Book seats for a planetarium show.")
    public String bookSeats(@ToolParam(description = "the date, as YYYY-MM-DD") String date,
                            @ToolParam(description = "the show's start time, like 16:00") String time,
                            @ToolParam(description = "how many seats, 1 to 6") int seats,
                            @ToolParam(description = "the visitor's name") String visitorName) {
        return bookings.book(visitorName, date, time, seats);
    }
}
