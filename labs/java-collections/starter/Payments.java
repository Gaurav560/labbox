import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Payments {

    // TODO (task total_paise): the sum of every payment's amountPaise
    public static long totalPaise(List<Payment> payments) {
        return 0;
    }

    // TODO (task totals_by_merchant): merchant name -> total paise
    public static Map<String, Long> totalsByMerchant(List<Payment> payments) {
        return new HashMap<>();
    }

    // TODO (task unique_merchants): every merchant once, A to Z
    public static List<String> uniqueMerchants(List<Payment> payments) {
        return new ArrayList<>();
    }

    // TODO (task top_merchants): the n merchants with the biggest totals, biggest first; ties A to Z
    public static List<String> topMerchants(List<Payment> payments, int n) {
        return new ArrayList<>();
    }

    public static void main(String[] args) {
        List<Payment> today = List.of(
                new Payment("Chai Point", 2000), new Payment("Kirana King", 15000), new Payment("Chai Point", 3000));
        System.out.println(totalPaise(today));        // 20000
        System.out.println(totalsByMerchant(today));  // {Chai Point=5000, Kirana King=15000}
        System.out.println(uniqueMerchants(today));   // [Chai Point, Kirana King]
        System.out.println(topMerchants(today, 1));   // [Kirana King]
    }
}
