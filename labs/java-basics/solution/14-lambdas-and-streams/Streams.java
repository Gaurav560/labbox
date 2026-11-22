import java.util.Comparator;
import java.util.List;

// Chapter 14: lambdas and streams.
public class Streams {
    public static List<Integer> passing(List<Integer> marks) {
        return marks.stream().filter(m -> m >= 40).toList();
    }

    public static List<String> sortByLength(List<String> words) {
        return words.stream()
                .sorted(Comparator.comparing(String::length).thenComparing(Comparator.naturalOrder()))
                .toList();
    }

    public static void main(String[] args) {
        System.out.println(passing(List.of(72, 30, 90, 40, 39)));
        System.out.println(sortByLength(List.of("banana", "fig", "apple", "kiwi", "date")));
    }
}
