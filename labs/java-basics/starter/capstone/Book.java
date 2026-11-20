package capstone;

/** Inherited from a colleague who has left. Two copies of the same book end up twice in a HashSet. */
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

    // TODO (task fix_book): equals compares ISBNs, but something it needs is missing. Find it and add it.
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Book other)) return false;
        return isbn.equals(other.isbn);
    }
}
