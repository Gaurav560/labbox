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

    @Tool(description = "Book seats for a planetarium show.", requiresConfirmation = true)
    public String bookSeats(@ToolParam(description = "the date, as YYYY-MM-DD") String date,
                            @ToolParam(description = "the show's start time, like 16:00") String time,
                            @ToolParam(description = "how many seats, 1 to 6") int seats,
                            ToolContext context) {
        String visitor = (String) context.getContext().get("visitor");
        return bookings.book(visitor, date, time, seats);
    }
}
