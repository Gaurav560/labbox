import loops.Loops;

public class CheckLoops {
    public static void main(String[] a) {
        try {
            int[][] cases = {{5, 15}, {1, 1}, {0, 0}, {-3, 0}, {100, 5050}};
            boolean ok = true;
            for (int[] c : cases) {
                int got = Loops.sumTo(c[0]);
                if (got != c[1]) {
                    T.fail("sum_to", "sumTo(" + c[0] + ") gave " + got + ", but it should be " + c[1] + ".", c[1], got);
                    ok = false;
                    break;
                }
            }
            if (ok) T.pass("sum_to");
        } catch (Throwable e) { T.crashed("sum_to", e); }
        try {
            String[] in = {"Hello World", "AEIOU", "rhythm", "", "Java is fun"};
            int[] want = {3, 5, 0, 0, 4};
            for (int i = 0; i < in.length; i++) {
                int got = Loops.countVowels(in[i]);
                if (got != want[i]) {
                    String why = in[i].equals("AEIOU") && got == 0 ? " Upper-case vowels count too: lower-case each character first." : "";
                    T.fail("count_vowels", "countVowels(" + T.show(in[i]) + ") gave " + got + ", but it should be " + want[i] + "." + why, want[i], got);
                    return;
                }
            }
            T.pass("count_vowels");
        } catch (Throwable e) { T.crashed("count_vowels", e); }
    }
}
