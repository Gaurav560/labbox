import java.io.IOException;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;

// Chapter 15: files.
public class Expenses {
    // TODO (task read_totals): {category: total} from a CSV with the header date,category,amount, rounded
    // to 2 decimals; skip rows with a missing or bad amount; a missing file throws NoSuchFileException.
    public static Map<String, Double> readTotals(Path path) throws IOException {
        return new HashMap<>();
    }

    public static void main(String[] args) throws IOException {
        Map<String, Double> totals = readTotals(Path.of("expenses.csv"));
        System.out.println(totals.size() + " categories, rent " + totals.get("rent"));
    }
}
