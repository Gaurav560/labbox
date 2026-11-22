// Chapter 8: one array, two names.
import java.util.Arrays;

public class SameArray {
    public static void main(String[] args) {
        int[] mine = {1, 2, 3};
        int[] yours = mine;
        yours[0] = 99;
        System.out.println(Arrays.toString(mine));
    }
}
