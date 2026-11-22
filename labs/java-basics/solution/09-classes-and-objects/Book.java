// Chapter 9: Shelf's first class. One class, many book objects, each with its own copies.
public class Book {
    private final String title;
    private int copies;

    public Book(String title, int copies) {
        this.title = title;
        this.copies = copies;
    }

    public boolean borrow() {
        if (copies == 0) {
            return false;
        }
        copies = copies - 1;
        return true;
    }

    public String describe() {
        return title + " (" + copies + " on the shelf)";
    }

    public static void main(String[] args) {
        Book hobbit = new Book("The Hobbit", 2);
        Book dune = new Book("Dune", 1);
        hobbit.borrow();
        System.out.println(hobbit.describe());
        System.out.println(dune.describe());
        System.out.println(dune.borrow() + " " + dune.borrow());
    }
}
