package collections;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

/** Chapter 9: lists. */
public class ListTools {
    public static List<Integer> topN(List<Integer> numbers, int n) {
        List<Integer> copy = new ArrayList<>(numbers);
        copy.sort(Comparator.reverseOrder());
        return new ArrayList<>(copy.subList(0, Math.min(n, copy.size())));
    }
}
