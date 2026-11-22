// Chapter 12: one record that can hold any two types.
import java.util.List;

public class Pair {
    record Two<A, B>(A first, B second) { }

    static <T> T firstOr(List<T> items, T fallback) {
        return items.isEmpty() ? fallback : items.get(0);
    }

    public static void main(String[] args) {
        Two<String, Integer> shelf = new Two<>("Dune", 4);
        Two<String, Boolean> late = new Two<>("Emma", true);
        System.out.println(shelf + " " + late);
        int number = shelf.second();
        System.out.println(number + 1);
        System.out.println(firstOr(List.of("Asha", "Riya"), "nobody") + " " + firstOr(List.<String>of(), "nobody"));
    }
}
