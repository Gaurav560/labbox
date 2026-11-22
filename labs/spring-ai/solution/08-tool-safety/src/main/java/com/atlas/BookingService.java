package com.atlas;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

import org.springframework.stereotype.Service;

/** The planetarium's bookings. In a real museum this would be the ticketing system's database. */
@Service
public class BookingService {

    /** One booking: who, which show, how many seats. */
    public record Booking(String visitor, String date, String time, int seats) {}

    private final Map<String, Integer> freeSeats = new ConcurrentHashMap<>();
    private final List<Booking> bookings = new CopyOnWriteArrayList<>();

    /** Books seats, or refuses with a reason the model can pass on. */
    public synchronized String book(String visitor, String date, String time, int seats) {
        if (seats < 1 || seats > 6) {
            throw new IllegalArgumentException("A booking is for 1 to 6 seats.");
        }
        String show = date + " " + time;
        int free = freeSeats.getOrDefault(show, 20);
        if (seats > free) {
            throw new IllegalStateException("Only " + free + " seats are free for the " + time + " show on " + date + ".");
        }
        freeSeats.put(show, free - seats);
        bookings.add(new Booking(visitor, date, time, seats));
        return "Booked " + seats + " seats for " + visitor + " at the " + time + " show on " + date + ".";
    }

    public List<Booking> bookings() {
        return List.copyOf(bookings);
    }
}
