// Chapter 14: the same rule written three ways, from 2004 Java to today's.
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

public class OldAndNew {
    public static void main(String[] args) {
        List<String> titles = new ArrayList<>(List.of("Emma", "It", "Dune", "Ulysses"));

        titles.sort(new Comparator<String>() {
            @Override
            public int compare(String a, String b) {
                return a.length() - b.length();
            }
        });
        System.out.println(titles);

        titles.sort((a, b) -> b.length() - a.length());
        System.out.println(titles);

        titles.sort(Comparator.comparing(String::length));
        System.out.println(titles);
    }
}
