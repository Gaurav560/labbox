package collections;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** Chapter 9: maps. */
public class WordCounter {
    public static Map<String, Integer> count(List<String> words) {
        Map<String, Integer> counts = new HashMap<>();
        for (String w : words) {
            String key = w.toLowerCase();
            counts.put(key, counts.getOrDefault(key, 0) + 1);
        }
        return counts;
    }
}
