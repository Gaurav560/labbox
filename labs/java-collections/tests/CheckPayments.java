import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.function.Supplier;

/** Hidden checks for java-collections. Prints one @@RESULT line per task; never prints the solution. */
public class CheckPayments {
    static String esc(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n");
    }

    static void report(String task, boolean passed, String message, Object expected, Object actual) {
        String extra = expected == null ? "" : ", \"expected\": \"" + esc(String.valueOf(expected)) + "\", \"actual\": \"" + esc(String.valueOf(actual)) + "\"";
        System.out.println("@@RESULT {\"task\": \"" + task + "\", \"passed\": " + passed + ", \"message\": \"" + esc(message) + "\"" + extra + "}");
    }

    static <T> void check(String task, String call, Supplier<T> run, T want) {
        try {
            T got = run.get();
            if (!Objects.equals(got, want)) {
                report(task, false, call + " returned " + got, want, got);
                return;
            }
            report(task, true, "ok", null, null);
        } catch (Throwable t) {
            report(task, false, call + " threw " + t.getClass().getSimpleName() + (t.getMessage() != null ? ": " + t.getMessage() : ""), null, null);
        }
    }

    static Payment p(String m, long a) {
        return new Payment(m, a);
    }

    public static void main(String[] args) {
        List<Payment> day = List.of(p("Chai Point", 2000), p("Kirana King", 15000), p("Chai Point", 3000),
                p("Annapurna Mess", 15000), p("Bata Footwear", 499900), p("Chai Point", 1));
        List<Payment> none = List.of();

        check("total_paise", "totalPaise(today)", () -> Payments.totalPaise(day), 534901L);
        if (Payments.totalPaise(none) != 0) report("total_paise", false, "totalPaise of no payments should be 0", 0, Payments.totalPaise(none));

        check("totals_by_merchant", "totalsByMerchant(today)", () -> Payments.totalsByMerchant(day),
                Map.of("Chai Point", 5001L, "Kirana King", 15000L, "Annapurna Mess", 15000L, "Bata Footwear", 499900L));

        check("unique_merchants", "uniqueMerchants(today)", () -> Payments.uniqueMerchants(day),
                List.of("Annapurna Mess", "Bata Footwear", "Chai Point", "Kirana King"));

        check("top_merchants", "topMerchants(today, 3)", () -> Payments.topMerchants(day, 3),
                List.of("Bata Footwear", "Annapurna Mess", "Kirana King"));
    }
}
