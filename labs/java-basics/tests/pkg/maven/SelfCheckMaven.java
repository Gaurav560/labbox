import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.stream.Stream;

/** Chapter 16: builds the learner's Maven project offline in a copy, then runs the jar. */
public class SelfCheckMaven {
    static String[] run(Path dir, int seconds, String... cmd) throws Exception {
        Process p = new ProcessBuilder(cmd).directory(dir.toFile()).redirectErrorStream(true).start();
        if (!p.waitFor(seconds, TimeUnit.SECONDS)) {
            p.destroyForcibly();
            return new String[] {"timed out after " + seconds + " seconds", "-1"};
        }
        return new String[] {new String(p.getInputStream().readAllBytes()), String.valueOf(p.exitValue())};
    }

    static void copy(Path from, Path to) throws IOException {
        try (Stream<Path> all = Files.walk(from)) {
            for (Path p : all.toList()) {
                Path rel = from.relativize(p);
                if (rel.toString().startsWith("target")) continue;
                Path dest = to.resolve(rel.toString());
                if (Files.isDirectory(p)) Files.createDirectories(dest);
                else Files.copy(p, dest);
            }
        }
    }

    static String tail(String s) {
        List<String> lines = s.lines().filter(l -> l.contains("ERROR") || l.contains("error:")).limit(4).toList();
        return String.join("\n", lines.isEmpty() ? s.lines().limit(4).toList() : lines);
    }

    public static void main(String[] a) {
        Path learner = Path.of(a[0]);
        boolean built = false;
        Path work = null;
        try {
            Path moved = learner.resolve("src/main/java/shelf/catalog/Catalog.java");
            if (!Files.isRegularFile(learner.resolve("pom.xml"))) {
                T.fail("package_catalog", "pom.xml is missing from 16-packages-and-maven/. Maven needs it to build the project.");
            } else if (!Files.isRegularFile(moved)) {
                T.fail("package_catalog", "Catalog.java is not in src/main/java/shelf/catalog/ yet. The folders must match the package: shelf.catalog lives in shelf/catalog/.");
            } else if (!Files.readString(moved).lines().anyMatch(l -> l.strip().equals("package shelf.catalog;"))) {
                T.fail("package_catalog", "Catalog.java is in the right folder, but its first code line should be: package shelf.catalog;");
            } else {
                work = Files.createTempDirectory("labbox-mvn");
                copy(learner, work);
                String[] r = run(work, 150, "mvn", "-o", "-q", "-B", "package");
                if (!r[1].equals("0")) {
                    T.fail("package_catalog", "Catalog is in its package, but mvn package failed:\n" + tail(r[0]) + "\nRun mvn -o -q package yourself to see the whole message.");
                } else {
                    built = true;
                    T.pass("package_catalog");
                }
            }
        } catch (Throwable e) { T.crashed("package_catalog", e); }
        try {
            if (!built) {
                T.fail("runnable_jar", "the project has to build first: finish the package task, then mvn package makes target/shelf.jar.");
                return;
            }
            String[] r = run(work, 30, Path.of(System.getProperty("java.home"), "bin", "java").toString(), "-jar", "target/shelf.jar");
            String out = r[0].strip();
            if (out.contains("no main manifest attribute")) {
                T.fail("runnable_jar", "java -jar target/shelf.jar says \"no main manifest attribute\": the jar does not know which class has main. Fill in <mainClass> in pom.xml.");
            } else if (out.contains("Could not find or load main class")) {
                T.fail("runnable_jar", "java -jar found a mainClass in pom.xml, but no such class: " + T.show(out.lines().findFirst().orElse("")) + ". Use the full name, package included.");
            } else if (!out.equals("Shelf 1.0: 2 books")) {
                T.fail("runnable_jar", "java -jar target/shelf.jar printed " + T.show(out) + ", but it should print \"Shelf 1.0: 2 books\".", "Shelf 1.0: 2 books", out);
            } else {
                T.pass("runnable_jar");
            }
        } catch (Throwable e) { T.crashed("runnable_jar", e); }
    }
}
