// Chapter 11: a list that grows, a map that looks things up, a set that keeps one of each.
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class Desk {
    public static void main(String[] args) {
        List<String> queue = new ArrayList<>();
        queue.add("Asha");
        queue.add("Kabir");
        queue.add("Riya");
        queue.remove("Kabir");
        System.out.println(queue + " " + queue.size() + " " + queue.get(0));

        Map<String, Integer> shelfOf = new HashMap<>();
        shelfOf.put("Dune", 3);
        shelfOf.put("The Hobbit", 1);
        shelfOf.put("Dune", 4);
        System.out.println(shelfOf.get("Dune") + " " + shelfOf.get("Emma") + " " + shelfOf.containsKey("Emma"));

        Set<String> visitors = new HashSet<>(List.of("Asha", "Riya", "Asha", "Asha"));
        System.out.println(visitors.size() + " " + visitors.contains("Riya"));
    }
}
