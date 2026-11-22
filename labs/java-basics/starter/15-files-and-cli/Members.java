// Chapter 15: read a whole text file, one line at a time.
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public class Members {
    public static void main(String[] args) throws IOException {
        Path path = Path.of("members.txt");
        List<String> lines = Files.readAllLines(path);
        System.out.println(lines.size() + " lines");
        for (String line : lines) {
            if (line.isBlank()) {
                continue;
            }
            String[] parts = line.split(",");
            System.out.println(parts[0] + " has " + parts[1] + " books");
        }
    }
}
