// Chapter 12: a sealed family of records, and a switch that handles every kind.
public class Kinds {
    sealed interface Item permits Book, Dvd, Atlas { }

    record Book(String title, int pages) implements Item { }

    record Dvd(String title, int minutes) implements Item { }

    record Atlas(String place) implements Item { }

    static String describe(Item item) {
        return switch (item) {
            case Book b when b.pages() > 500 -> b.title() + ": a long read";
            case Book b -> b.title() + ": " + b.pages() + " pages";
            case Dvd d -> d.title() + ": " + d.minutes() + " minutes";
            case Atlas a -> "an atlas of " + a.place();
        };
    }

    public static void main(String[] args) {
        System.out.println(describe(new Book("Dune", 612)));
        System.out.println(describe(new Book("Emma", 474)));
        System.out.println(describe(new Dvd("Planet Earth", 550)));
        System.out.println(describe(new Atlas("Goa")));
    }
}
