import errors.Ages;
import errors.InvalidAgeException;
import errors.SumResult;
import java.util.List;

public class CheckErrors {
    public static void main(String[] a) {
        checkParseAge();
        checkSafeSum();
    }

    static void checkParseAge() {
        try {
            String[] good = {"17", "0", "150", " 42 "};
            int[] want = {17, 0, 150, 42};
            for (int i = 0; i < good.length; i++) {
                int got = Ages.parseAge(good[i]);
                if (got != want[i]) {
                    T.fail("parse_age", "parseAge(" + T.show(good[i]) + ") gave " + got + ", but it should be " + want[i] + ".", want[i], got);
                    return;
                }
            }
            try {
                Ages.parseAge("abc");
                T.fail("parse_age", "parseAge(\"abc\") returned a number; it should throw InvalidAgeException.");
                return;
            } catch (InvalidAgeException e) {
                if (!(e.getCause() instanceof NumberFormatException)) {
                    T.fail("parse_age", "for \"abc\", pass the NumberFormatException as the cause: new InvalidAgeException(message, e).");
                    return;
                }
            }
            for (String bad : new String[] {"-1", "151", "12.5", ""}) {
                try {
                    Ages.parseAge(bad);
                    T.fail("parse_age", "parseAge(" + T.show(bad) + ") was accepted; it should throw InvalidAgeException.");
                    return;
                } catch (InvalidAgeException e) { /* expected */ }
            }
            T.pass("parse_age");
        } catch (Throwable e) { T.crashed("parse_age", e); }
    }

    static void checkSafeSum() {
        try {
            SumResult r = Ages.safeSum(List.of("10", "x", "2.5", ""));
            if (r.total() != 12.5 || !r.bad().equals(List.of("x", ""))) {
                T.fail("safe_sum", "safeSum([10, x, 2.5, \"\"]) gave " + r + ", but it should total 12.5 with bad values [x, \"\"].", "SumResult[total=12.5, bad=[x, ]]", r);
            } else if (Ages.safeSum(List.of()).total() != 0 || !Ages.safeSum(List.of()).bad().isEmpty()) {
                T.fail("safe_sum", "safeSum of an empty list should total 0 with no bad values.");
            } else {
                T.pass("safe_sum");
            }
        } catch (Throwable e) { T.crashed("safe_sum", e); }
    }
}
