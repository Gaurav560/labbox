package capstone;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** Chapter 13: the monthly report. */
public class Report {
    public static MonthlyReport monthly(Path path) throws IOException {
        List<String> lines = Files.readAllLines(path);
        Map<String, Double> per = new HashMap<>();
        List<Integer> bad = new ArrayList<>();
        double total = 0;
        int count = 0;
        for (int i = 1; i < lines.size(); i++) {
            String line = lines.get(i);
            if (line.isBlank()) {
                continue;
            }
            String[] parts = line.split(",", -1);
            double amount;
            try {
                if (parts.length != 3 || parts[1].isBlank()) throw new NumberFormatException();
                amount = Double.parseDouble(parts[2]);
            } catch (NumberFormatException e) {
                bad.add(i + 1);
                continue;
            }
            per.merge(parts[1], amount, Double::sum);
            total += amount;
            count++;
        }
        per.replaceAll((k, v) -> Math.round(v * 100) / 100.0);
        double rounded = Math.round(total * 100) / 100.0;
        double average = count == 0 ? 0 : Math.round(total / count * 100) / 100.0;
        return new MonthlyReport(rounded, count, average, per, bad);
    }
}
