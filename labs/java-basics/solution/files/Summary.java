package files;

import java.io.IOException;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/** Chapter 12: a command-line program. java files.Summary expenses.csv --top 3 */
public class Summary {
    public static void main(String[] args) throws IOException {
        if (args.length == 0) {
            System.err.println("Usage: Summary <file.csv> [--top N]");
            System.exit(2);
        }
        int top = 3;
        if (args.length >= 3 && args[1].equals("--top")) {
            top = Integer.parseInt(args[2]);
        }
        Map<String, Double> totals;
        try {
            totals = Expenses.readTotals(Path.of(args[0]));
        } catch (NoSuchFileException e) {
            System.err.println("File not found: " + args[0]);
            System.exit(1);
            return;
        }
        List<Map.Entry<String, Double>> rows = new ArrayList<>(totals.entrySet());
        rows.sort(Map.Entry.<String, Double>comparingByValue().reversed());
        for (int i = 0; i < Math.min(top, rows.size()); i++) {
            System.out.printf("%s: %.2f%n", rows.get(i).getKey(), rows.get(i).getValue());
        }
    }
}
