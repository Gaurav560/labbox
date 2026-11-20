import arrays.ArrayTools;
import java.util.Arrays;

public class CheckArrays {
    public static void main(String[] a) {
        try {
            int[][] in = {{3, 9, 2}, {-5, -2, -9}, {7}};
            int[] want = {9, -2, 7};
            boolean ok = true;
            for (int i = 0; i < in.length; i++) {
                int got = ArrayTools.max(in[i]);
                if (got != want[i]) {
                    String why = in[i][0] < 0 && got == 0 ? " Starting the best value at 0 fails for all-negative arrays: start with the first item." : "";
                    T.fail("array_max", "max(" + Arrays.toString(in[i]) + ") gave " + got + ", but it should be " + want[i] + "." + why, want[i], got);
                    ok = false;
                    break;
                }
            }
            if (ok) {
                try {
                    ArrayTools.max(new int[0]);
                    T.fail("array_max", "max of an empty array returned a number; it should throw an IllegalArgumentException.");
                } catch (IllegalArgumentException e) {
                    T.pass("array_max");
                }
            }
        } catch (Throwable e) { T.crashed("array_max", e); }
        try {
            int[] input = {1, 2, 3, 4};
            int[] got = ArrayTools.reversed(input);
            if (!Arrays.equals(input, new int[] {1, 2, 3, 4})) {
                T.fail("reversed", "reversed changed the array it was given: it is now " + Arrays.toString(input) + ". Write into a new array instead.", "[1, 2, 3, 4]", Arrays.toString(input));
            } else if (got == input) {
                T.fail("reversed", "reversed gave back the same array object; make a new one with new int[numbers.length].");
            } else if (!Arrays.equals(got, new int[] {4, 3, 2, 1}) || ArrayTools.reversed(new int[0]).length != 0) {
                T.fail("reversed", "reversed([1, 2, 3, 4]) gave " + Arrays.toString(got) + ", but it should be [4, 3, 2, 1].", "[4, 3, 2, 1]", Arrays.toString(got));
            } else {
                T.pass("reversed");
            }
        } catch (Throwable e) { T.crashed("reversed", e); }
    }
}
