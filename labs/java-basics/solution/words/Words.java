package words;

import java.util.ArrayList;
import java.util.List;

/** Chapter 5: strings. */
public class Words {
    public static int countWords(String text) {
        String t = text.trim();
        if (t.isEmpty()) {
            return 0;
        }
        return t.split("\\s+").length;
    }

    public static String cleanName(String raw) {
        String t = raw.trim();
        if (t.isEmpty()) {
            return "";
        }
        List<String> parts = new ArrayList<>();
        for (String w : t.split("\\s+")) {
            parts.add(w.substring(0, 1).toUpperCase() + w.substring(1).toLowerCase());
        }
        return String.join(" ", parts);
    }
}
