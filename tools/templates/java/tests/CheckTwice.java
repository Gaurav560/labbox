import java.lang.reflect.Method;

/** Hidden checks. Prints one @@RESULT line per task; never prints the solution. */
public class CheckTwice {
    static void report(String task, boolean passed, String message, String expected, String actual) {
        String extra = expected == null ? "" : ", \"expected\": \"" + expected + "\", \"actual\": \"" + actual + "\"";
        System.out.println("@@RESULT {\"task\": \"" + task + "\", \"passed\": " + passed + ", \"message\": \"" + message + "\"" + extra + "}");
    }

    public static void main(String[] args) {
        try {
            Method m = Class.forName("Twice").getMethod("twice", int.class);
            int[][] cases = {{21, 42}, {0, 0}, {-3, -6}};
            for (int[] c : cases) {
                Object got = m.invoke(null, c[0]);
                if (!Integer.valueOf(c[1]).equals(got)) {
                    report("twice", false, "twice(" + c[0] + ") returned " + got, String.valueOf(c[1]), String.valueOf(got));
                    return;
                }
            }
            report("twice", true, "ok", null, null);
        } catch (Throwable t) {
            report("twice", false, "Could not run Twice.twice(int): " + t.getClass().getSimpleName(), null, null);
        }
    }
}
