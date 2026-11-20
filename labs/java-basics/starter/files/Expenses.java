package files;

import java.io.IOException;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;

/** Chapter 12: files. */
public class Expenses {
    // TODO (task read_totals): {category: total} from a CSV with the header date,category,amount, rounded
    // to 2 decimals; skip rows with a missing or bad amount; a missing file throws NoSuchFileException.
    public static Map<String, Double> readTotals(Path path) throws IOException {
        return new HashMap<>();
    }
}
