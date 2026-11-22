import java.util.Map;
import java.util.Objects;

/** Shared by every chapter's check: one @@RESULT line per task, in the LabBox voice (Content standard). */
public class T {
    static final Map<String, String> PASS = Map.ofEntries(
        Map.entry("hello_shelf", "Shelf said its first words: a class, a main method and two println lines. Every Java program starts like this."),
        Map.entry("fix_first_errors", "Two compile errors read and fixed. Java checks the whole file before it runs a single line, and its messages point at the exact spot."),
        Map.entry("fix_total_fines", "Found it: the loop started at position 1 and skipped the first fine. Off-by-one bugs are everywhere, and now you can catch one."),
        Map.entry("fix_can_borrow", "Fixed: at the limit there is no room left. Boundaries (> or >=) are where bugs love to hide; printing the values made it visible."),
        Map.entry("percent", "Right, including 0 out of 0. Casting to double before dividing avoids Java's integer division trap."),
        Map.entry("format_rupees", "Spot on: %02d keeps the paise at two digits, so 5 paise shows as 0.05."),
        Map.entry("grade", "All the edges are right: 80, 79, 40, 39 and the invalid marks."),
        Map.entry("leap_year", "Correct for 1900 and 2000 too: three rules in one boolean expression."),
        Map.entry("sum_to", "Correct, and a loop that never runs leaves 0, so negative n is handled for free."),
        Map.entry("count_vowels", "Nice: one character at a time, and upper and lower case treated the same."),
        Map.entry("count_words", "Correct even with tabs, new lines and an empty text. The \\\\s+ pattern does the hard work."),
        Map.entry("clean_name", "Tidy: trimmed, single spaces, and every word capitalised."),
        Map.entry("array_max", "Right, and an empty array gets a clear exception instead of a wrong answer."),
        Map.entry("reversed", "A new array, and the caller's array left exactly as it was. Good habit."),
        Map.entry("point_distance", "Correct: a record keeps x and y, and your method uses them."),
        Map.entry("bank_account", "Your account protects itself: bad amounts are refused and the balance can only change through its methods. That is encapsulation."),
        Map.entry("areas", "Both shapes know their own area: each class answers in its own way."),
        Map.entry("total_area", "One method for every Shape, including shapes nobody has written yet. That is the power of an interface."),
        Map.entry("top_n", "Biggest first, and the caller's list untouched: you sorted a copy."),
        Map.entry("word_counts", "Correct counts: getOrDefault is the classic way to count with a map."),
        Map.entry("parse_age", "Clear, checked exceptions with the original cause kept inside. Callers know exactly what went wrong."),
        Map.entry("safe_sum", "Robust: good values added, bad ones reported, nothing crashes."),
        Map.entry("passing", "Filtered with a lambda: the stream reads almost like the sentence it implements."),
        Map.entry("sort_by_length", "Shortest first and ties alphabetical: comparators chain neatly."),
        Map.entry("read_totals", "You read a messy real file without crashing, and a missing file comes back as a proper exception."),
        Map.entry("summary_cli", "A real command-line program: clean output, a friendly message and exit code 1 when the file is missing."),
        Map.entry("fix_book", "Fixed one of Java's most famous bugs: equal objects now have equal hash codes, so HashSet and HashMap work."),
        Map.entry("monthly_report", "A complete report from messy data, with the right line numbers. You have finished Java from zero: well done.")
    );

    static String esc(String s) {
        if (s == null) return "null";
        StringBuilder b = new StringBuilder();
        for (char c : s.toCharArray()) {
            switch (c) {
                case '"' -> b.append("\\\"");
                case '\\' -> b.append("\\\\");
                case '\n' -> b.append("\\n");
                case '\r' -> b.append("\\r");
                case '\t' -> b.append("\\t");
                default -> {
                    if (c < 0x20) b.append(String.format("\\u%04x", (int) c));
                    else b.append(c);
                }
            }
        }
        return b.toString();
    }

    static void pass(String task) {
        emit(task, true, PASS.getOrDefault(task, "ok"), null, null);
    }

    static void fail(String task, String message) {
        emit(task, false, "Not yet: " + message, null, null);
    }

    static void fail(String task, String message, Object expected, Object actual) {
        emit(task, false, "Not yet: " + message, show(expected), show(actual));
    }

    static void emit(String task, boolean passed, String message, String expected, String actual) {
        String extra = expected == null ? "" : ", \"expected\": \"" + esc(expected) + "\", \"actual\": \"" + esc(actual) + "\"";
        System.out.println("@@RESULT {\"task\": \"" + esc(task) + "\", \"passed\": " + passed
                + ", \"message\": \"" + esc(message) + "\"" + extra + "}");
        System.out.flush();
    }

    static String show(Object o) {
        if (o == null) return "null";
        if (o instanceof String s) return "\"" + s + "\"";
        if (o instanceof int[] a) return java.util.Arrays.toString(a);
        return String.valueOf(o);
    }

    static boolean same(Object a, Object b) {
        return Objects.equals(a, b);
    }

    /** A crash in the learner's code becomes a failed task with the exception named, never a dead check. */
    static void crashed(String task, Throwable e) {
        e.printStackTrace();
        fail(task, "your code threw " + e.getClass().getSimpleName() + (e.getMessage() != null ? ": " + e.getMessage() : "") + ". See Output for the line.");
    }
}
