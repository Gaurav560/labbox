package loops;

/** Chapter 4: loops. */
public class Loops {
    public static int sumTo(int n) {
        int total = 0;
        for (int i = 1; i <= n; i++) {
            total += i;
        }
        return total;
    }

    public static int countVowels(String text) {
        int count = 0;
        for (char c : text.toCharArray()) {
            if ("aeiou".indexOf(Character.toLowerCase(c)) >= 0) {
                count++;
            }
        }
        return count;
    }
}
