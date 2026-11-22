import java.net.URL;
import java.net.URLClassLoader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

/** Chapter 17: the learner's FinesTest must pass on the real lateFee and catch three planted bugs;
 *  Renewals.canRenew must be fixed. Tests run with JUnit's console launcher from the offline repository. */
public class SelfCheckTesting {
    static final String JUNIT = "/opt/m2/org/junit/platform/junit-platform-console-standalone/1.11.4/junit-platform-console-standalone-1.11.4.jar";
    static final Path VARIANTS = Path.of("/check/tests/pkg/testing/fines");
    static final String JAVA_BIN = Path.of(System.getProperty("java.home"), "bin").toString();

    static String[] run(int seconds, List<String> cmd) throws Exception {
        Process p = new ProcessBuilder(cmd).redirectErrorStream(true).start();
        if (!p.waitFor(seconds, TimeUnit.SECONDS)) {
            p.destroyForcibly();
            return new String[] {"timed out after " + seconds + " seconds", "-1"};
        }
        return new String[] {new String(p.getInputStream().readAllBytes()), String.valueOf(p.exitValue())};
    }

    /** Compiles one Fines variant with the learner's FinesTest and runs it: {output, exit code}; exit 0 means all passed. */
    static String[] runTests(String variant, Path learnerTest) throws Exception {
        Path out = Files.createTempDirectory("labbox-junit-" + variant);
        List<String> javac = new ArrayList<>(List.of(JAVA_BIN + "/javac", "-cp", JUNIT, "-d", out.toString(),
                VARIANTS.resolve(variant).resolve("Fines.java").toString(), learnerTest.toString()));
        String[] c = run(60, javac);
        if (!c[1].equals("0")) {
            return new String[] {c[0], "compile"};
        }
        return run(60, List.of(JAVA_BIN + "/java", "-jar", JUNIT, "execute", "--disable-banner", "--details=tree",
                "--fail-if-no-tests", "--class-path", out.toString(), "--select-class", "shelf.FinesTest"));
    }

    static String firstFailure(String out) {
        return out.lines().map(String::strip).filter(l -> l.contains("AssertionFailedError") || l.contains("=>") || l.contains("Exception"))
                .findFirst().orElse("see Output");
    }

    public static void main(String[] a) {
        Path learner = Path.of(a[0]);
        try {
            Path test = learner.resolve("src/test/java/shelf/FinesTest.java");
            if (!Files.isRegularFile(test)) {
                T.fail("test_late_fee", "src/test/java/shelf/FinesTest.java is missing. Your tests for lateFee go there.");
            } else {
                String[] good = runTests("good", test);
                if (good[1].equals("compile")) {
                    System.out.println(good[0]);
                    T.fail("test_late_fee", "FinesTest.java does not compile. See Output for the line, or run mvn -o -q test.");
                } else if (!good[1].equals("0")) {
                    System.out.println(good[0]);
                    T.fail("test_late_fee", "your tests fail on the correct lateFee, so one of them expects the wrong number: " + firstFailure(good[0]) + ". Work it out from the rules again: 2 a day for 7 days, then 5 a day, at most 100.");
                } else if (!runTests("nocap", test)[1].equals("1")) {
                    T.fail("test_late_fee", "your tests all pass even when lateFee forgets the 100 rupee limit (a whole year late would cost 1804). Add a test for a book that is very late.");
                } else if (!runTests("lateweek", test)[1].equals("1")) {
                    T.fail("test_late_fee", "your tests all pass even when the higher rate starts a day too late (8 days late gives 16 instead of 19). Test the day just after the first week.");
                } else if (!runTests("negative", test)[1].equals("1")) {
                    T.fail("test_late_fee", "your tests all pass even when lateFee quietly returns 0 for -1 days instead of refusing it. Test that a negative number throws, with assertThrows.");
                } else {
                    T.pass("test_late_fee");
                }
            }
        } catch (Throwable e) { T.crashed("test_late_fee", e); }
        try {
            Path src = learner.resolve("src/main/java/shelf/Renewals.java");
            Path out = Files.createTempDirectory("labbox-renewals");
            String[] c = run(60, List.of(JAVA_BIN + "/javac", "-d", out.toString(), src.toString()));
            if (!c[1].equals("0")) {
                System.out.println(c[0]);
                T.fail("fix_renewal", "Renewals.java does not compile. See Output for the line.");
                return;
            }
            try (URLClassLoader loader = new URLClassLoader(new URL[] {out.toUri().toURL()})) {
                var m = loader.loadClass("shelf.Renewals").getMethod("canRenew", int.class, boolean.class);
                Object[][] cases = {{0, false, true}, {1, false, true}, {2, false, false}, {3, false, false}, {0, true, false}, {1, true, false}};
                for (Object[] cs : cases) {
                    boolean got = (boolean) m.invoke(null, cs[0], cs[1]);
                    if (got != (boolean) cs[2]) {
                        T.fail("fix_renewal", "canRenew(" + cs[0] + ", " + cs[1] + ") gave " + got + ", but it should be " + cs[2] + ". A loan may be renewed at most twice, never while reserved.", cs[2], got);
                        return;
                    }
                }
                T.pass("fix_renewal");
            }
        } catch (Throwable e) { T.crashed("fix_renewal", e); }
    }
}
