import java.util.ArrayList;
import java.util.List;

// Chapter 13: exceptions.
public class Ages {
    public static int parseAge(String text) throws InvalidAgeException {
        int age;
        try {
            age = Integer.parseInt(text.trim());
        } catch (NumberFormatException e) {
            throw new InvalidAgeException("not a whole number: \"" + text + "\"", e);
        }
        if (age < 0 || age > 150) {
            throw new InvalidAgeException("age out of range: " + age);
        }
        return age;
    }

    public static SumResult safeSum(List<String> values) {
        double total = 0;
        List<String> bad = new ArrayList<>();
        for (String v : values) {
            try {
                total += Double.parseDouble(v.trim());
            } catch (NumberFormatException e) {
                bad.add(v);
            }
        }
        return new SumResult(total, bad);
    }

    public static void main(String[] args) {
        try {
            System.out.println(parseAge(" 42 "));
            System.out.println(parseAge("twelve"));
        } catch (InvalidAgeException e) {
            System.out.println("refused: " + e.getMessage() + " (cause: " + e.getCause() + ")");
        }
        SumResult r = safeSum(List.of("10", "x", "2.5", ""));
        System.out.println(r.total() + " " + r.bad());
    }
}
