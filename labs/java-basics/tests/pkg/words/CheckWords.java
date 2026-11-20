import words.Words;

public class CheckWords {
    public static void main(String[] a) {
        try {
            String[] in = {"Java is fun", "  lots   of   spaces  ", "", "   ", "hello, world", "tab\tand\nnew line"};
            int[] want = {3, 3, 0, 0, 2, 4};
            boolean ok = true;
            for (int i = 0; i < in.length; i++) {
                int got = Words.countWords(in[i]);
                if (got != want[i]) {
                    String why = got > want[i] ? " split(\" \") makes empty pieces for extra spaces; trim, then split on \\\\s+." : "";
                    T.fail("count_words", "countWords(" + T.show(in[i]) + ") gave " + got + ", but it should be " + want[i] + "." + why, want[i], got);
                    ok = false;
                    break;
                }
            }
            if (ok) T.pass("count_words");
        } catch (Throwable e) { T.crashed("count_words", e); }
        try {
            String[] in = {"  riya   SHARMA ", "ARJUN", "   ", "meera\tnair", "a b"};
            String[] want = {"Riya Sharma", "Arjun", "", "Meera Nair", "A B"};
            for (int i = 0; i < in.length; i++) {
                String got = Words.cleanName(in[i]);
                if (!want[i].equals(got)) {
                    T.fail("clean_name", "cleanName(" + T.show(in[i]) + ") gave " + T.show(got) + ", but it should be " + T.show(want[i]) + ".", want[i], got);
                    return;
                }
            }
            T.pass("clean_name");
        } catch (Throwable e) { T.crashed("clean_name", e); }
    }
}
