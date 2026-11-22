import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class CheckCapstone {
    public static void main(String[] a) {
        try {
            Set<Book> shelf = new HashSet<>();
            shelf.add(new Book("978-0134685991", "Effective Java"));
            shelf.add(new Book("978-0134685991", "Effective Java"));
            Map<Book, String> loans = new HashMap<>();
            loans.put(new Book("111", "Go"), "Riya");
            if (shelf.size() != 1) {
                T.fail("fix_book", "two equal books in a HashSet gave a set of " + shelf.size() + ". A HashSet uses hashCode first: equal books need equal hash codes.", 1, shelf.size());
            } else if (!"Riya".equals(loans.get(new Book("111", "Go")))) {
                T.fail("fix_book", "a HashMap could not find a book by an equal key; hashCode must use the same field as equals.");
            } else {
                T.pass("fix_book");
            }
        } catch (Throwable e) { T.crashed("fix_book", e); }
        try {
            Path dir = Files.createTempDirectory("labbox-report");
            Path small = dir.resolve("g.csv");
            Files.writeString(small, "date,category,amount\n2026-03-02,food,120\n2026-03-03,,45\n2026-03-03,travel,abc\n2026-03-04,rent,18000\n");
            MonthlyReport r = Report.monthly(small);
            MonthlyReport want = new MonthlyReport(18120.0, 2, 9060.0, Map.of("food", 120.0, "rent", 18000.0), List.of(3, 4));
            Path blank = dir.resolve("b.csv");
            Files.writeString(blank, "date,category,amount\n2026-03-01,food,10\n\n2026-03-02,food,x\n2026-03-03,fun,20.5\n");
            MonthlyReport rb = Report.monthly(blank);
            MonthlyReport wantB = new MonthlyReport(30.5, 2, 15.25, Map.of("food", 10.0, "fun", 20.5), List.of(4));
            MonthlyReport re = Report.monthly(Files.writeString(dir.resolve("e.csv"), "date,category,amount\n"));
            if (!want.equals(r)) {
                T.fail("monthly_report", "for the five lines in the chapter the report is " + r + ", but it should be " + want + ".", want, r);
            } else if (!wantB.equals(rb)) {
                T.fail("monthly_report", "with a blank line before a bad row, the report is " + rb + "; line numbers must count the blank line too (it is line 3).", wantB, rb);
            } else if (re.count() != 0 || re.total() != 0 || re.average() != 0 || !re.badLines().isEmpty()) {
                T.fail("monthly_report", "a file with only the header should give zeros and no bad lines; got " + re + ".");
            } else {
                T.pass("monthly_report");
            }
        } catch (Throwable e) { T.crashed("monthly_report", e); }
    }
}
