import java.util.List;
import java.util.Map;

// Chapter 18: what the report contains.
public record MonthlyReport(double total, int count, double average, Map<String, Double> perCategory, List<Integer> badLines) {
}
