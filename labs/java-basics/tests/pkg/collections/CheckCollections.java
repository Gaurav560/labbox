import collections.ListTools;
import collections.WordCounter;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class CheckCollections {
    public static void main(String[] a) {
        try {
            List<Integer> marks = new ArrayList<>(List.of(72, 45, 90, 66));
            List<Integer> got = ListTools.topN(marks, 2);
            if (!marks.equals(List.of(72, 45, 90, 66))) {
                T.fail("top_n", "topN changed the list it was given: it is now " + marks + ". Sort a copy: new ArrayList<>(numbers).", "[72, 45, 90, 66]", marks);
            } else if (!List.of(90, 72).equals(got)) {
                String why = List.of(45, 66).equals(got) ? " That is the smallest first: sort biggest first with Comparator.reverseOrder()." : "";
                T.fail("top_n", "topN([72, 45, 90, 66], 2) gave " + got + ", but it should be [90, 72]." + why, "[90, 72]", got);
            } else if (!ListTools.topN(new ArrayList<>(List.of(5, 1)), 5).equals(List.of(5, 1)) || !ListTools.topN(new ArrayList<>(List.of(3, 1)), 0).isEmpty()) {
                T.fail("top_n", "asking for more numbers than there are (or for 0) should work: keep at most n with Math.min.");
            } else {
                T.pass("top_n");
            }
        } catch (Throwable e) { T.crashed("top_n", e); }
        try {
            Map<String, Integer> got = WordCounter.count(List.of("juice", "Coffee", "JUICE", "juice"));
            Map<String, Integer> want = Map.of("juice", 3, "coffee", 1);
            if (!want.equals(got)) {
                T.fail("word_counts", "count([juice, Coffee, JUICE, juice]) gave " + got + ", but it should be " + want + ". Lower-case each word before counting.", want, got);
            } else if (!WordCounter.count(List.of()).isEmpty()) {
                T.fail("word_counts", "count of no words should be an empty map.");
            } else {
                T.pass("word_counts");
            }
        } catch (Throwable e) { T.crashed("word_counts", e); }
    }
}
