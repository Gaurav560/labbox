// Chapter 14: a stream does nothing until you ask for a result.
import java.util.List;
import java.util.stream.Stream;

public class Lazy {
    public static void main(String[] args) {
        Stream<String> s = List.of("Dune", "Emma", "It").stream()
                .filter(t -> {
                    System.out.println("  checking " + t);
                    return t.length() > 2;
                });
        System.out.println("pipeline built");
        System.out.println(s.findFirst().get());
    }
}
