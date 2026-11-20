package errors;

import java.util.ArrayList;
import java.util.List;

/** Chapter 10: exceptions. */
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
}
