package com.setu;

import java.util.List;

/** Chapter 4: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) {
        for (String text : new String[] {"Lonavala", "When does the Ghat Express leave Pune?",
                "पुणे ते लोणावळा गाडी किती वाजता आहे?", "Pune to Lonavala train kitne baje hai?", "🚆🚆🚆"}) {
            System.out.println(Tokens.count(text) + " tokens, " + text.length() + " characters: " + text);
        }

        List<String> chat = List.of(
                "Passenger: Hello! I am travelling with my grandmother next Sunday.",
                "Setu: Hello! How can I help you plan the trip?",
                "Passenger: We want the morning train from Pune to Lonavala.",
                "Setu: The Ghat Express leaves Pune at 7:15 and reaches Lonavala at 8:40.",
                "Passenger: Can she get a lower berth?");
        System.out.println("\nWith a budget of 40 tokens, the model sees:");
        Context.fit(chat, 40).forEach(m -> System.out.println("  " + m));
    }
}
