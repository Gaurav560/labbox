import java.util.HashMap;
import java.util.List;
import java.util.Map;

// Chapter 11: maps.
public class WordCounter {
    // TODO (task word_counts): {word in lower case: how many times}.
    public static Map<String, Integer> count(List<String> words) {
        return new HashMap<>();
    }

    public static void main(String[] args) {
        System.out.println(count(List.of("juice", "Coffee", "JUICE", "juice")));
    }
}
