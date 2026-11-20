import files.Expenses;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

public class CheckFiles {
    static Path temp(String name, String text) throws IOException {
        Path dir = Files.createTempDirectory("labbox-check");
        Path p = dir.resolve(name);
        Files.writeString(p, text);
        return p;
    }

    static String[] run(String... args) throws Exception {
        String java = Path.of(System.getProperty("java.home"), "bin", "java").toString();
        List<String> cmd = new java.util.ArrayList<>(List.of(java, "-cp", System.getProperty("labbox.build"), "files.Summary"));
        cmd.addAll(List.of(args));
        Process p = new ProcessBuilder(cmd).start();
        if (!p.waitFor(20, TimeUnit.SECONDS)) {
            p.destroyForcibly();
            return new String[] {"", "timed out", "-1"};
        }
        return new String[] {new String(p.getInputStream().readAllBytes()), new String(p.getErrorStream().readAllBytes()), String.valueOf(p.exitValue())};
    }

    public static void main(String[] a) {
        try {
            String sample = "date,category,amount\n2026-03-02,food,120\n2026-03-02,travel,40.50\n\n2026-03-03,food,80\n2026-03-04,food,abc\n2026-03-04,travel,\n";
            Map<String, Double> got = Expenses.readTotals(temp("e.csv", sample));
            Map<String, Double> want = Map.of("food", 200.0, "travel", 40.5);
            if (!want.equals(got)) {
                T.fail("read_totals", "on a file with a blank line, a bad amount and a missing amount, readTotals gave " + got + ", but it should be " + want + ".", want, got);
            } else if (!Expenses.readTotals(temp("h.csv", "date,category,amount\n")).isEmpty()) {
                T.fail("read_totals", "a file with only the header should give an empty map.");
            } else {
                try {
                    Expenses.readTotals(Path.of("/tmp/labbox-no-such-file.csv"));
                    T.fail("read_totals", "a missing file should throw NoSuchFileException (Files.readAllLines does that for you).");
                } catch (NoSuchFileException e) {
                    T.pass("read_totals");
                }
            }
        } catch (Throwable e) { T.crashed("read_totals", e); }
        try {
            String big = "date,category,amount\n2026-03-01,rent,18000\n2026-03-02,food,120\n2026-03-03,shopping,799\n2026-03-03,food,abc\n2026-03-04,travel,60\n2026-03-05,food,80.5\n2026-03-06,fun,350\n";
            Path data = temp("big.csv", big);
            String[] r2 = run(data.toString(), "--top", "2");
            String[] r3 = run(data.toString());
            String missing = "/tmp/labbox-missing.csv";
            String[] rm = run(missing);
            if (!r2[0].equals("rent: 18000.00\nshopping: 799.00\n")) {
                T.fail("summary_cli", "Summary big.csv --top 2 printed\n" + r2[0] + r2[1] + "\nbut it should print\nrent: 18000.00\nshopping: 799.00");
            } else if (!r3[0].equals("rent: 18000.00\nshopping: 799.00\nfun: 350.00\n")) {
                T.fail("summary_cli", "without --top it should print the top 3; it printed\n" + r3[0]);
            } else if (rm[1].contains("Exception") || !rm[1].contains("File not found: " + missing) || !rm[2].equals("1")) {
                T.fail("summary_cli", "for a missing file, System.err should say \"File not found: " + missing + "\" and the exit code be 1, with no stack trace; got " + T.show(rm[1].strip()) + " and exit code " + rm[2] + ".");
            } else {
                T.pass("summary_cli");
            }
        } catch (Throwable e) { T.crashed("summary_cli", e); }
    }
}
