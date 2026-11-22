// Chapter 5: one week of returned books. A loop visits every day, one at a time.
public class Week {
    public static void main(String[] args) {
        int[] returned = {12, 9, 15, 4, 20};

        for (int count : returned) {
            System.out.println("Returned: " + count);
        }

        System.out.println("Done: that was the whole week.");
    }
}
