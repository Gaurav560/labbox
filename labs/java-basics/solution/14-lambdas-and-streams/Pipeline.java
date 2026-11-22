// Chapter 14: a stream pipeline over Shelf's books.
import java.util.List;

public class Pipeline {
    record Book(String title, int pages, boolean overdue) { }

    public static void main(String[] args) {
        List<Book> books = List.of(
                new Book("Dune", 612, true),
                new Book("Emma", 474, false),
                new Book("Ulysses", 730, true),
                new Book("It", 1138, true));

        List<String> late = books.stream()
                .filter(b -> b.overdue())
                .map(b -> b.title().toUpperCase())
                .sorted()
                .toList();
        System.out.println(late);

        long count = books.stream().filter(Book::overdue).count();
        int pages = books.stream().mapToInt(Book::pages).sum();
        System.out.println(count + " overdue, " + pages + " pages in all");
        System.out.println(books.size());
    }
}
