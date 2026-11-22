
public class CheckTypes {
    public static void main(String[] a) {
        try {
            double[][] cases = {{45, 50, 90}, {1, 3, 33.3}, {2, 3, 66.7}, {0, 50, 0}, {7, 0, 0}, {50, 50, 100}};
            boolean ok = true;
            for (double[] c : cases) {
                double got = Numbers.percent((int) c[0], (int) c[1]);
                if (got != c[2]) {
                    String why = got == 0 && c[2] != 0 ? " Dividing two ints throws the fraction away: cast to double first." : "";
                    T.fail("percent", "percent(" + (int) c[0] + ", " + (int) c[1] + ") gave " + got + ", but it should be " + c[2] + "." + why, c[2], got);
                    ok = false;
                    break;
                }
            }
            if (ok) T.pass("percent");
        } catch (Throwable e) { T.crashed("percent", e); }
        try {
            int[] in = {1250, 5, 0, 120000, 99, 100};
            String[] want = {"₹12.50", "₹0.05", "₹0.00", "₹1200.00", "₹0.99", "₹1.00"};
            for (int i = 0; i < in.length; i++) {
                String got = Numbers.formatRupees(in[i]);
                if (!want[i].equals(got)) {
                    String why = got != null && got.endsWith("." + (in[i] % 100)) && in[i] % 100 < 10 ? " Pad the paise to two digits with %02d." : "";
                    T.fail("format_rupees", "formatRupees(" + in[i] + ") gave " + T.show(got) + ", but it should be " + T.show(want[i]) + "." + why, want[i], got);
                    return;
                }
            }
            T.pass("format_rupees");
        } catch (Throwable e) { T.crashed("format_rupees", e); }
    }
}
