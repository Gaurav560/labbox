package streams;

import java.util.Comparator;
import java.util.List;

/** Chapter 11: lambdas and streams. */
public class Streams {
    public static List<Integer> passing(List<Integer> marks) {
        return marks.stream().filter(m -> m >= 40).toList();
    }

    public static List<String> sortByLength(List<String> words) {
        return words.stream()
                .sorted(Comparator.comparing(String::length).thenComparing(Comparator.naturalOrder()))
                .toList();
    }
}
