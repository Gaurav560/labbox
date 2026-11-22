import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.io.StringWriter;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import javax.tools.JavaCompiler;
import javax.tools.ToolProvider;

/**
 * Chapter 1 compiles each file on its own: FixMe.java starts broken on purpose, and that must never stop
 * Hello.java's task from passing. Usage: java SelfCheckFirstProgram <chapter folder>.
 */
public class SelfCheckFirstProgram {
    record Run(boolean compiled, String errors, String out, Throwable crash) {}

    static Run run(Path folder, String name) throws Exception {
        Path src = folder.resolve(name + ".java");
        if (!Files.exists(src)) return null;
        Path out = Files.createTempDirectory("ch1-");
        JavaCompiler javac = ToolProvider.getSystemJavaCompiler();
        StringWriter err = new StringWriter();
        boolean ok = javac.getTask(err, null, null, List.of("-d", out.toString()), null,
                javac.getStandardFileManager(null, null, null).getJavaFileObjects(src.toFile())).call();
        if (!ok) return new Run(false, err.toString(), "", null);
        PrintStream old = System.out;
        ByteArrayOutputStream buf = new ByteArrayOutputStream();
        Throwable crash = null;
        try (URLClassLoader loader = new URLClassLoader(new URL[] {out.toUri().toURL()})) {
            System.setOut(new PrintStream(buf, true, "UTF-8"));
            loader.loadClass(name).getMethod("main", String[].class).invoke(null, (Object) new String[0]);
        } catch (java.lang.reflect.InvocationTargetException e) {
            crash = e.getCause();
        } finally {
            System.setOut(old);
        }
        return new Run(true, "", buf.toString("UTF-8"), crash);
    }

    static List<String> lines(String s) {
        return s.strip().isEmpty() ? List.of() : s.strip().lines().map(String::stripTrailing).toList();
    }

    public static void main(String[] a) throws Exception {
        Path folder = Path.of(a[0]);
        List<String> want = List.of("Hello! I am Shelf.", "I will look after your books.");
        Run hello = run(folder, "Hello");
        if (hello == null) T.fail("hello_shelf", "Could not find 01-first-program/Hello.java in your workspace.");
        else if (!hello.compiled()) T.fail("hello_shelf", "Hello.java does not compile yet. Run java Hello.java in the terminal: Java shows the line and a ^ under the problem.");
        else if (hello.crash() != null) T.fail("hello_shelf", "Hello.java stopped with " + hello.crash() + ".");
        else {
            List<String> got = lines(hello.out());
            if (got.equals(want)) T.pass("hello_shelf");
            else if (got.isEmpty()) T.fail("hello_shelf", "Hello.java ran but printed nothing. Lines that start with // are notes for people; Java skips them. Add System.out.println(...) lines inside main.", String.join("\n", want), "");
            else if (got.size() < 2) T.fail("hello_shelf", "Hello.java printed one line; Shelf should say two. Each println prints one line.", String.join("\n", want), String.join("\n", got));
            else if (String.join("\n", got).equalsIgnoreCase(String.join("\n", want))) T.fail("hello_shelf", "So close: the words are right, but a capital letter differs. Java prints exactly what is between the quotes.", String.join("\n", want), String.join("\n", got));
            else T.fail("hello_shelf", "The lines differ from what Shelf should say. Compare them letter by letter, including the full stops.", String.join("\n", want), String.join("\n", got));
        }
        List<String> want2 = List.of("Shelf is starting...", "Ready to look after your books.", "Books on the shelf: 12");
        Run fix = run(folder, "FixMe");
        if (fix == null) T.fail("fix_first_errors", "Could not find 01-first-program/FixMe.java in your workspace.");
        else if (!fix.compiled()) {
            String e = fix.errors();
            if (e.contains("';' expected")) T.fail("fix_first_errors", "Java still finds a missing ; at the end of a line, so it does not compile. Run java FixMe.java: the ^ shows where.");
            else if (e.contains("package system does not exist")) T.fail("fix_first_errors", "One mistake fixed. Now Java does not know system: Java is case-sensitive, and the class is called System.");
            else T.fail("fix_first_errors", "FixMe.java does not compile yet: " + e.lines().findFirst().orElse("see the terminal") + ".");
        } else if (fix.crash() != null) T.fail("fix_first_errors", "FixMe.java stopped with " + fix.crash() + ".");
        else if (!lines(fix.out()).equals(want2)) T.fail("fix_first_errors", "It compiles now, but the lines changed. Fix only the two mistakes and keep the words as they were.", String.join("\n", want2), fix.out().strip());
        else T.pass("fix_first_errors");
    }
}
