import java.util.List;

// Chapter 13: exceptions.
public class Ages {
    // TODO (task parse_age): a whole number from 0 to 150; anything else throws InvalidAgeException
    // (with the NumberFormatException as its cause when the text is not a number).
    public static int parseAge(String text) throws InvalidAgeException {
        return 0;
    }

    // TODO (task safe_sum): add up the values that are numbers; list the ones that are not.
    public static SumResult safeSum(List<String> values) {
        return new SumResult(0, List.of());
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
