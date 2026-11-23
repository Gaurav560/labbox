package com.setu;

import dev.langchain4j.service.AiServices;

/** Chapter 15: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) {
        Reader reader = AiServices.create(Reader.class, Models.structuredModel(System.getenv("OPENAI_BASE_URL"),
                System.getenv("OPENAI_API_KEY")));
        TripRequest trip = reader.trip("Hi, I need 3 tickets from Pune to Karjat this coming Saturday morning please");
        System.out.println(trip);
        System.out.println("passengers + 1 = " + (trip.passengers() + 1));

        for (String m : new String[] {"The 7:15 was 40 minutes late again and nobody announced anything!",
                "Can I carry a bicycle on the Konkan Breeze?", "I cancelled yesterday, where is my money?",
                "Does the Monsoon Mail stop at Khandala?"}) {
            System.out.println(reader.topic(m) + "  <- " + m);
        }
    }
}
