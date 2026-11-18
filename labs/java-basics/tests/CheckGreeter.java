import java.lang.reflect.Method;

/** Hidden checks for java-basics. Prints one @@RESULT line per task. */
public class CheckGreeter {

    static String esc(String s) {
        if (s == null) return "null";
        StringBuilder b = new StringBuilder();
        for (char c : s.toCharArray()) {
            switch (c) {
                case '"': b.append("\\\""); break;
                case '\\': b.append("\\\\"); break;
                case '\n': b.append("\\n"); break;
                case '\r': b.append("\\r"); break;
                case '\t': b.append("\\t"); break;
                default:
                    if (c < 0x20) b.append(String.format("\\u%04x", (int) c));
                    else b.append(c);
            }
        }
        return b.toString();
    }

    static void report(String task, boolean passed, String message) {
        report(task, passed, message, null, null);
    }

    /** expected and actual are optional v2 fields; the UI shows them side by side. */
    static void report(String task, boolean passed, String message, String expected, String actual) {
        String extra = expected == null ? "" : ", \"expected\": \"" + esc(expected) + "\", \"actual\": \"" + esc(actual) + "\"";
        System.out.println("@@RESULT {\"task\": \"" + esc(task) + "\", \"passed\": " + passed
                + ", \"message\": \"" + esc(message) + "\"" + extra + "}");
        System.out.flush();
    }

    static String show(Object o) {
        return o == null ? "null" : (o instanceof String ? "\"" + o + "\"" : String.valueOf(o));
    }

    static String describe(Throwable t) {
        Throwable c = t;
        if (c instanceof java.lang.reflect.InvocationTargetException && c.getCause() != null) c = c.getCause();
        return c.getClass().getSimpleName() + (c.getMessage() != null ? ": " + c.getMessage() : "");
    }

    static void checkGreet() {
        try {
            Method m = Class.forName("Greeter").getMethod("greet", String.class);
            String[][] cases = {{"Asha", "Hello, Asha!"}, {"World", "Hello, World!"}, {"", "Hello, !"}};
            for (String[] c : cases) {
                Object got = m.invoke(null, c[0]);
                if (!c[1].equals(got)) {
                    report("greet", false, "greet(\"" + c[0] + "\") returned " + show(got) + ", expected " + show(c[1]),
                            show(c[1]), show(got));
                    return;
                }
            }
            report("greet", true, "ok");
        } catch (NoSuchMethodException | ClassNotFoundException e) {
            report("greet", false, "Could not find a method public static String greet(String) in class Greeter");
        } catch (Throwable t) {
            report("greet", false, "greet threw " + describe(t));
        }
    }

    static void checkLongestWord() {
        try {
            Method m = Class.forName("Greeter").getMethod("longestWord", String.class);
            Object[][] cases = {
                {"the quick brown fox", 5},
                {"hello", 5},
                {"a bb ccc dd", 3},
                {"Java is fun", 4},
                {"", 0},
            };
            for (Object[] c : cases) {
                Object got = m.invoke(null, c[0]);
                if (!c[1].equals(got)) {
                    report("longest_word", false, "longestWord(\"" + c[0] + "\") returned " + show(got) + ", expected " + c[1],
                            show(c[1]), show(got));
                    return;
                }
            }
            report("longest_word", true, "ok");
        } catch (NoSuchMethodException | ClassNotFoundException e) {
            report("longest_word", false, "Could not find a method public static int longestWord(String) in class Greeter");
        } catch (Throwable t) {
            report("longest_word", false, "longestWord threw " + describe(t));
        }
    }

    public static void main(String[] args) {
        checkGreet();
        checkLongestWord();
    }
}
