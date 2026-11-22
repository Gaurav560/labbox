// Chapter 8: a row of shelves, with the number of books on each.
import java.util.Arrays;

public class Shelves {
    public static void main(String[] args) {
        int[] books = {12, 30, 7, 25};
        System.out.println(books.length);
        System.out.println(books[0] + " " + books[3]);
        books[2] = 9;
        System.out.println(Arrays.toString(books));
        int[] empty = new int[3];
        String[] names = new String[2];
        System.out.println(Arrays.toString(empty) + " " + Arrays.toString(names));
    }
}
