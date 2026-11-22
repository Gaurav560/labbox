import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// Chapter 15: files.
public class Expenses {
    public static Map<String, Double> readTotals(Path path) throws IOException {
        List<String> lines = Files.readAllLines(path);
        Map<String, Double> totals = new HashMap<>();
        for (int i = 1; i < lines.size(); i++) {
            String[] parts = lines.get(i).split(",", -1);
            if (parts.length != 3 || parts[1].isBlank()) {
                continue;
            }
            try {
                totals.merge(parts[1], Double.parseDouble(parts[2]), Double::sum);
            } catch (NumberFormatException e) {
                // a bad amount: skip the row
            }
        }
        totals.replaceAll((k, v) -> Math.round(v * 100) / 100.0);
        return totals;
    }

    public static void main(String[] args) throws IOException {
        Map<String, Double> totals = readTotals(Path.of("expenses.csv"));
        System.out.println(totals.size() + " categories, rent " + totals.get("rent"));
    }
}
