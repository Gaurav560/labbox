import java.util.ArrayList;
import java.util.List;

public class CheckStreams {
    public static void main(String[] a) {
        try {
            List<Integer> got = Streams.passing(List.of(72, 30, 90, 40, 39));
            if (!List.of(72, 90, 40).equals(got)) {
                String why = got != null && got.equals(List.of(72, 90)) ? " 40 itself passes: use >=." : "";
                T.fail("passing", "passing([72, 30, 90, 40, 39]) gave " + got + ", but it should be [72, 90, 40]." + why, "[72, 90, 40]", got);
            } else {
                T.pass("passing");
            }
        } catch (Throwable e) { T.crashed("passing", e); }
        try {
            List<String> words = new ArrayList<>(List.of("banana", "fig", "apple", "kiwi", "date"));
            List<String> got = Streams.sortByLength(words);
            List<String> want = List.of("fig", "date", "kiwi", "apple", "banana");
            if (!words.equals(List.of("banana", "fig", "apple", "kiwi", "date"))) {
                T.fail("sort_by_length", "sortByLength changed the list it was given; sort a stream or a copy instead.");
            } else if (!want.equals(got)) {
                String why = got != null && got.equals(List.of("fig", "kiwi", "date", "apple", "banana")) ? " Ties need an order: thenComparing alphabetically." : "";
                T.fail("sort_by_length", "sortByLength gave " + got + ", but it should be " + want + "." + why, want, got);
            } else {
                T.pass("sort_by_length");
            }
        } catch (Throwable e) { T.crashed("sort_by_length", e); }
    }
}
