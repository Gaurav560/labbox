package com.setu.check;

import org.junit.jupiter.api.Test;

import com.setu.Learn;
import com.setu.Rules;

class Ch01Check {

    @Test
    void ruleReply() {
        R.task("rule_reply", () -> {
            String refund = "Refunds: the full fare up to 24 hours before departure, half the fare after that.";
            String luggage = "Each passenger may carry 40 kg of luggage free of charge.";
            String pets = "Small pets travel in the guard's van, with a pet ticket of Rs 120.";
            String unknown = "Sorry, I don't know that yet. Please ask at the station office.";
            String[][] cases = {
                {"How do I get a refund?", refund}, {"REFUND please", refund},
                {"Can I bring two bags?", luggage}, {"Is my luggage free?", luggage},
                {"Can my dog come?", pets}, {"Are PETS allowed?", pets},
                {"What time is it?", unknown}};
            for (String[] c : cases) {
                String got = Rules.reply(c[0]);
                if (!c[1].equals(got)) {
                    String why = c[0].equals("REFUND please") || c[0].equals("Are PETS allowed?")
                            ? "Capitals must not matter: lower-case the question first (toLowerCase), then look for the keyword."
                            : "Check the keywords: refund; luggage or bag; pet or dog; anything else gets UNKNOWN.";
                    R.fail("rule_reply", "Rules.reply(\"" + c[0] + "\") gave the wrong answer. " + why, c[1], String.valueOf(got));
                    return;
                }
            }
            R.pass("rule_reply", "Your rules answer every question they were written for, in any capitals. Now ask them about a suitcase.");
        });
    }

    static int reference(int[] late, boolean[] complained) {
        int best = Integer.MAX_VALUE, fewest = Integer.MAX_VALUE;
        for (int c : late) {
            int wrong = Learn.mistakes(c, late, complained);
            if (wrong < fewest || (wrong == fewest && c < best)) {
                best = c;
                fewest = wrong;
            }
        }
        return best;
    }

    @Test
    void learnThreshold() {
        R.task("learn_threshold", () -> {
            int[][] lates = {
                {0, 2, 5, 8, 12, 15, 18, 25, 30, 45},
                {40, 3, 20, 7, 33, 1},
                {10, 20, 30, 40}};
            boolean[][] complaints = {
                {false, false, false, false, true, false, true, true, true, true},
                {true, false, true, false, true, false},
                {false, true, false, true}};
            for (int i = 0; i < lates.length; i++) {
                int want = reference(lates[i], complaints[i]);
                int got = Learn.bestThreshold(lates[i], complaints[i]);
                if (got != want) {
                    String hint = i == 2
                            ? "In this data two thresholds make the same number of mistakes: return the smaller one."
                            : "Try each value of minutesLate as the threshold, count its mistakes with mistakes(...), keep the one with the fewest.";
                    R.fail("learn_threshold", "Learn.bestThreshold(" + java.util.Arrays.toString(lates[i]) + ", ...) is not the best threshold. " + hint,
                            String.valueOf(want), String.valueOf(got));
                    return;
                }
            }
            R.pass("learn_threshold", "You did not write the rule; the examples chose it. That is machine learning, at its smallest.");
        });
    }
}
