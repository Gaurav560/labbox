import decisions.Decisions;

public class CheckDecisions {
    public static void main(String[] a) {
        try {
            int[] in = {95, 80, 79, 60, 59, 40, 39, 100, 0, 101, -1};
            String[] want = {"A", "A", "B", "B", "C", "C", "F", "A", "F", "Invalid", "Invalid"};
            boolean ok = true;
            for (int i = 0; i < in.length; i++) {
                String got = Decisions.grade(in[i]);
                if (!want[i].equals(got)) {
                    String why = (in[i] == 80 || in[i] == 60 || in[i] == 40) ? " Check the boundary: use >=, not >." : "";
                    T.fail("grade", "grade(" + in[i] + ") gave " + T.show(got) + ", but it should be " + T.show(want[i]) + "." + why, want[i], got);
                    ok = false;
                    break;
                }
            }
            if (ok) T.pass("grade");
        } catch (Throwable e) { T.crashed("grade", e); }
        try {
            int[] in = {2024, 2023, 1900, 2000, 2100, 1600, 2019};
            boolean[] want = {true, false, false, true, false, true, false};
            for (int i = 0; i < in.length; i++) {
                boolean got = Decisions.isLeapYear(in[i]);
                if (got != want[i]) {
                    String why = (in[i] == 1900 || in[i] == 2100) ? " Years divisible by 100 are not leap years, unless they are divisible by 400." : "";
                    T.fail("leap_year", "isLeapYear(" + in[i] + ") gave " + got + ", but it should be " + want[i] + "." + why, want[i], got);
                    return;
                }
            }
            T.pass("leap_year");
        } catch (Throwable e) { T.crashed("leap_year", e); }
    }
}
