package com.setu;

/** Chapter 1: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) {
        System.out.println("== Rules, written by hand");
        for (String q : new String[] {"How do I get a refund?", "Can my dog travel with me?",
                "Can I bring two bags?", "How heavy can my suitcase be?"}) {
            System.out.println(q + "\n  -> " + Rules.reply(q));
        }

        System.out.println("\n== A rule, learned from examples");
        // Last week's trains: minutes late, and whether a passenger complained.
        int[] late = {0, 2, 5, 8, 12, 15, 18, 25, 30, 45};
        boolean[] complained = {false, false, false, false, true, false, true, true, true, true};
        int t = Learn.bestThreshold(late, complained);
        System.out.println("Learned: late by " + t + " minutes or more means a complaint ("
                + Learn.mistakes(t, late, complained) + " of " + late.length + " examples wrong)");
    }
}
