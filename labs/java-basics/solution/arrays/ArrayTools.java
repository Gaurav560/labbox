package arrays;

/** Chapter 6: arrays. */
public class ArrayTools {
    public static int max(int[] numbers) {
        if (numbers.length == 0) {
            throw new IllegalArgumentException("max of an empty array");
        }
        int best = numbers[0];
        for (int n : numbers) {
            if (n > best) {
                best = n;
            }
        }
        return best;
    }

    public static int[] reversed(int[] numbers) {
        int[] out = new int[numbers.length];
        for (int i = 0; i < numbers.length; i++) {
            out[i] = numbers[numbers.length - 1 - i];
        }
        return out;
    }
}
