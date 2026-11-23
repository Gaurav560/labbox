package com.setu;

import java.time.Clock;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.temporal.TemporalAdjusters;
import java.util.Locale;
import java.util.Map;

import dev.langchain4j.agent.tool.P;
import dev.langchain4j.agent.tool.Tool;

/** Java methods the model may call: facts and arithmetic it must never guess. */
public class RailTools {

    static final Map<String, Integer> FARES = Map.of("lonavala", 90, "karjat", 140, "ratnagiri", 420);

    private final Clock clock;

    public RailTools() {
        this(Clock.systemDefaultZone());
    }

    public RailTools(Clock clock) {
        this.clock = clock;
    }

    @Tool("The fare in rupees for one adult ticket from Pune to a station. Children under 5 travel free.")
    public int fare(@P("destination station: Lonavala, Karjat or Ratnagiri") String destination) {
        Integer fare = FARES.get(destination.trim().toLowerCase(Locale.ROOT));
        if (fare == null) {
            throw new IllegalArgumentException("Sahyadri Rail does not go to " + destination);
        }
        return fare;
    }

    // TODO (task date_tool): make this a tool the model can call, and make it work.
    //   Annotate it with @Tool("The date (YYYY-MM-DD) of the next given day of the week, after today") and the
    //   parameter with @P("day of the week in English, for example SATURDAY").
    //   Then: DayOfWeek.valueOf(the day, trimmed and upper-cased), and return
    //   LocalDate.now(clock).with(TemporalAdjusters.next(day)).toString().
    public String nextDate(String dayOfWeek) {
        return "";
    }
}
