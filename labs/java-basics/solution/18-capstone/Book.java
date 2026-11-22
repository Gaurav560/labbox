import java.util.HashSet;
import java.util.Objects;
import java.util.Set;

// Chapter 18: a library book, equal by ISBN, with a matching hashCode.
public class Book {
    private final String isbn;
    private final String title;

    public Book(String isbn, String title) {
        this.isbn = isbn;
        this.title = title;
    }

    public String getTitle() {
        return title;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Book other)) return false;
        return isbn.equals(other.isbn);
    }

    @Override
    public int hashCode() {
        return Objects.hash(isbn);
    }

    public static void main(String[] args) {
        Book a = new Book("978-0261102217", "The Hobbit");
        Book b = new Book("978-0261102217", "The Hobbit");
        Set<Book> shelf = new HashSet<>();
        shelf.add(a);
        shelf.add(b);
        System.out.println("equal: " + a.equals(b));
        System.out.println("same hash code: " + (a.hashCode() == b.hashCode()));
        System.out.println("books in the set: " + shelf.size());
    }
}
