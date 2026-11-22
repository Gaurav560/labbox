package com.atlas;

import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.temporal.TemporalAdjusters;
import java.util.List;

import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Component;

/** Facts about the museum that the model may ask for. The model never sees this code: only each tool's
 *  name, description and parameters. When it needs a fact, it asks; Spring AI calls the method and sends the result back. */
@Component
public class MuseumTools {

    /** One planetarium show: when it starts, and how many seats are still free. */
    public record Show(String time, String title, int freeSeats) {}

    private final ShowSchedule schedule;

    public MuseumTools(ShowSchedule schedule) {
        this.schedule = schedule;
    }

    @Tool(description = "Today's date, as YYYY-MM-DD, and its day of the week.")
    public String today() {
        LocalDate now = LocalDate.now();
        return now + " (" + now.getDayOfWeek() + ")";
    }

    @Tool(description = "The date of the next given day of the week, counting today. Use it for 'this Saturday' or 'next Monday'.")
    public String nextDay(@ToolParam(description = "a day of the week in capitals, like SATURDAY") String dayOfWeek) {
        LocalDate date = LocalDate.now().with(TemporalAdjusters.nextOrSame(DayOfWeek.valueOf(dayOfWeek.trim().toUpperCase())));
        return date + " (" + date.getDayOfWeek() + ")";
    }

    @Tool(description = "The museum's opening hours on one date. The museum is closed on Mondays.")
    public String openingHours(@ToolParam(description = "the date, as YYYY-MM-DD") String date) {
        LocalDate day = LocalDate.parse(date);
        if (day.getDayOfWeek() == DayOfWeek.MONDAY) {
            return "Closed on " + date + " (the museum is closed on Mondays).";
        }
        return "Open on " + date + " from 10:00 to 18:00. Last entry at 17:00.";
    }

    @Tool(description = "The planetarium shows on one date, with their start times and free seats.")
    public List<Show> planetariumShows(@ToolParam(description = "the date, as YYYY-MM-DD") String date) {
        return schedule.showsOn(LocalDate.parse(date));
    }

}
