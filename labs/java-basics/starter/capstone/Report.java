package capstone;

import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

/** Chapter 13: the monthly report. */
public class Report {
    // TODO (task monthly_report): total, count, average, per category and the bad line numbers.
    public static MonthlyReport monthly(Path path) throws IOException {
        return new MonthlyReport(0, 0, 0, Map.of(), List.of());
    }
}
