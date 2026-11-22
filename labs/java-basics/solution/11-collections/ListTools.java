import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

// Chapter 11: lists.
public class ListTools {
    public static List<Integer> topN(List<Integer> numbers, int n) {
        List<Integer> copy = new ArrayList<>(numbers);
        copy.sort(Comparator.reverseOrder());
        return new ArrayList<>(copy.subList(0, Math.min(n, copy.size())));
    }

    public static void main(String[] args) {
        System.out.println(topN(List.of(72, 45, 90, 66), 2));
    }
}
