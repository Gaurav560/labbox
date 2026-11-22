package com.atlas;

import java.time.DayOfWeek;
import java.time.LocalDate;
import java.util.List;

import org.springframework.stereotype.Service;

/** The planetarium's timetable. In a real museum this would come from the ticketing system's database. */
@Service
public class ShowSchedule {

    public List<MuseumTools.Show> showsOn(LocalDate date) {
        if (date.getDayOfWeek() == DayOfWeek.MONDAY) {
            return List.of();
        }
        boolean weekend = date.getDayOfWeek() == DayOfWeek.SATURDAY || date.getDayOfWeek() == DayOfWeek.SUNDAY;
        return List.of(
                new MuseumTools.Show("11:00", "Journey to the Moon", weekend ? 4 : 37),
                new MuseumTools.Show("14:00", "The Life of Stars", weekend ? 0 : 52),
                new MuseumTools.Show("16:00", "Black Holes", weekend ? 11 : 60));
    }
}
