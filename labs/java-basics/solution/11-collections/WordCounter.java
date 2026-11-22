import java.util.HashMap;
import java.util.List;
import java.util.Map;

// Chapter 11: maps.
public class WordCounter {
    public static Map<String, Integer> count(List<String> words) {
        Map<String, Integer> counts = new HashMap<>();
        for (String w : words) {
            String key = w.toLowerCase();
            counts.put(key, counts.getOrDefault(key, 0) + 1);
        }
        return counts;
    }

    public static void main(String[] args) {
        System.out.println(count(List.of("juice", "Coffee", "JUICE", "juice")));
    }
}
