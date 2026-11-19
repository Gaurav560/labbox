import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeSet;

public class Payments {

    public static long totalPaise(List<Payment> payments) {
        long total = 0;
        for (Payment p : payments) {
            total += p.amountPaise();
        }
        return total;
    }

    public static Map<String, Long> totalsByMerchant(List<Payment> payments) {
        Map<String, Long> totals = new HashMap<>();
        for (Payment p : payments) {
            totals.merge(p.merchant(), p.amountPaise(), Long::sum);
        }
        return totals;
    }

    public static List<String> uniqueMerchants(List<Payment> payments) {
        TreeSet<String> names = new TreeSet<>();
        for (Payment p : payments) {
            names.add(p.merchant());
        }
        return new ArrayList<>(names);
    }

    public static List<String> topMerchants(List<Payment> payments, int n) {
        return totalsByMerchant(payments).entrySet().stream()
                .sorted(Map.Entry.<String, Long>comparingByValue().reversed().thenComparing(Map.Entry.comparingByKey()))
                .limit(n)
                .map(Map.Entry::getKey)
                .toList();
    }

    public static void main(String[] args) {
        List<Payment> today = List.of(
                new Payment("Brew Point", 2000), new Payment("Kirana King", 15000), new Payment("Brew Point", 3000));
        System.out.println(totalPaise(today));
        System.out.println(totalsByMerchant(today));
        System.out.println(uniqueMerchants(today));
        System.out.println(topMerchants(today, 1));
    }
}
