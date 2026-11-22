/** Chapter 6: two quiet bugs in Fines.java. */
public class CheckFines {
    public static void main(String[] a) {
        try {
            int[][] in = {{10, 20, 30}, {50}, {}, {5, 5}, {0, 0, 7}};
            int[] want = {60, 50, 0, 10, 7};
            boolean ok = true;
            for (int i = 0; i < in.length; i++) {
                int got = Fines.totalFines(in[i]);
                if (got != want[i]) {
                    String arr = java.util.Arrays.toString(in[i]);
                    int rest = 0;
                    for (int k = 1; k < in[i].length; k++) rest += in[i][k];
                    String why = in[i].length > 0 && got == rest ? " The first fine is missing from the total. Print i inside the loop: which positions does it visit?" : "";
                    T.fail("fix_total_fines", "totalFines(" + arr + ") gave " + got + ", but it should be " + want[i] + "." + why, want[i], got);
                    ok = false;
                    break;
                }
            }
            if (ok) T.pass("fix_total_fines");
        } catch (Throwable e) { T.crashed("fix_total_fines", e); }
        try {
            int[][] in = {{4, 5}, {5, 5}, {6, 5}, {0, 1}, {0, 0}};
            boolean[] want = {true, false, false, true, false};
            boolean ok = true;
            for (int i = 0; i < in.length; i++) {
                boolean got = Fines.canBorrow(in[i][0], in[i][1]);
                if (got != want[i]) {
                    String why = in[i][0] == in[i][1] && got ? " At the limit there is no room left: room is 0. Print room and look at the comparison." : "";
                    T.fail("fix_can_borrow", "canBorrow(" + in[i][0] + ", " + in[i][1] + ") gave " + got + ", but it should be " + want[i] + "." + why, want[i], got);
                    ok = false;
                    break;
                }
            }
            if (ok) T.pass("fix_can_borrow");
        } catch (Throwable e) { T.crashed("fix_can_borrow", e); }
    }
}
