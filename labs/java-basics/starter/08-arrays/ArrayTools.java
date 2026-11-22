// Chapter 8: arrays.
public class ArrayTools {
    // TODO (task array_max): the biggest number; an empty array throws IllegalArgumentException.
    public static int max(int[] numbers) {
        return 0;
    }

    // TODO (task reversed): a NEW array with the numbers in reverse order; never change numbers.
    public static int[] reversed(int[] numbers) {
        return numbers;
    }

    public static void main(String[] args) {
        System.out.println(max(new int[] {3, 9, 2}));
        System.out.println(java.util.Arrays.toString(reversed(new int[] {1, 2, 3})));
    }
}
