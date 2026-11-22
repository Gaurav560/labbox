import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

// Chapter 18: the monthly report.
public class Report {
    // TODO (task monthly_report): total, count, average, per category and the bad line numbers.
    public static MonthlyReport monthly(Path path) throws IOException {
        return new MonthlyReport(0, 0, 0, Map.of(), List.of());
    }

    public static void main(String[] args) throws IOException {
        MonthlyReport r = monthly(Path.of("expenses.csv"));
        System.out.println("total " + r.total() + ", " + r.count() + " rows, average " + r.average());
        System.out.println("rent " + r.perCategory().get("rent") + ", food " + r.perCategory().get("food"));
        System.out.println("bad lines " + r.badLines());
    }
}
