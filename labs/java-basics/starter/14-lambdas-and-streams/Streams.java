import java.util.List;

// Chapter 14: lambdas and streams.
public class Streams {
    // TODO (task passing): the marks of 40 or more, in their original order.
    public static List<Integer> passing(List<Integer> marks) {
        return List.of();
    }

    // TODO (task sort_by_length): shortest first; words of the same length in alphabetical order.
    public static List<String> sortByLength(List<String> words) {
        return words;
    }

    public static void main(String[] args) {
        System.out.println(passing(List.of(72, 30, 90, 40, 39)));
        System.out.println(sortByLength(List.of("banana", "fig", "apple", "kiwi", "date")));
    }
}
